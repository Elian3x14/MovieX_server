from rest_framework import generics, status
from drf_spectacular.utils import extend_schema
from rest_framework import permissions
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django.http import HttpResponseBadRequest
from django.http import JsonResponse
import json
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db.models import Q
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

import requests
import hmac
import hashlib
import time
from django.conf import settings
from decimal import Decimal


from ..serializers import BookingSerializer, BookingDetailSerializer
from ..models import Booking, Showtime, BookingSeat, Seat
from ..payments import create_zalopay_payment

import logging

logger = logging.getLogger(__name__)


@extend_schema(tags=["Bookings"])
class BookingGetOrCreateView(generics.CreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        showtime_id = request.data.get("showtime")

        if not showtime_id:
            raise ValidationError({"showtime": "This field is required."})

        try:
            showtime = Showtime.objects.get(id=showtime_id)
        except Showtime.DoesNotExist:
            raise ValidationError({"showtime": "Showtime does not exist."})

        # Kiểm tra xem đã có booking đang pending chưa (và chưa hết hạn)
        existing_booking = Booking.objects.filter(
            user=user,
            showtime=showtime,
            status="pending",
            expired_at__gt=timezone.now(),
        ).first()

        if existing_booking:
            serializer = self.get_serializer(existing_booking)
            return Response(serializer.data)

        # Nếu không có thì tạo mới
        booking = Booking.objects.create(
            user=user,
            showtime=showtime,
            status="pending",
            total_amount=0,
            expired_at=timezone.now() + timezone.timedelta(minutes=5),
        )

        serializer = self.get_serializer(booking)
        return Response(serializer.data)


@extend_schema(tags=["Bookings"])
class BookingDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]


@extend_schema(tags=["Bookings"])
class AddBookingSeatView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, booking_id, seat_id):
        # TODO: Kiểm tra có chừa ra ghế đơn trong hàng không?
        user = request.user
        booking = get_object_or_404(Booking, id=booking_id)

        if booking.user != user:
            return Response({"error": "Permission denied."}, status=403)

        try:
            seat = Seat.objects.get(id=seat_id)
        except Seat.DoesNotExist:
            return Response({"error": "Seat does not exist."}, status=400)

        if BookingSeat.objects.filter(booking=booking, seat=seat).exists():
            return Response({"message": "Seat already added to booking."}, status=200)

        # Kiểm tra xem ghế đã bị người khác đặt chưa
        now = timezone.now()
        if (
            BookingSeat.objects.filter(seat=seat, booking__showtime=booking.showtime)
            .filter(
                Q(booking__status="paid")
                | Q(booking__status="pending", booking__expired_at__gt=now)
            )
            .exists()
        ):
            return Response({"error": "Seat already booked."}, status=400)

        BookingSeat.objects.create(booking=booking, seat=seat)

        self._notify_ws(booking.showtime.id, seat_id, user.id)

        return Response({"seat_added": seat_id}, status=201)

    def _notify_ws(self, showtime_id, seat_id, sender_id):
        channel_layer = get_channel_layer()
        group_name = f"booking_{showtime_id}"
        logger.info(f"send to group name: {group_name}")
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "seat_added",
                "message": {
                    "seat_id": seat_id,
                    "sender_id": sender_id,  # Thêm ID của người gửi để xử lý sau
                },
            },
        )


@extend_schema(tags=["Bookings"])
class RemoveBookingSeatView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, booking_id, seat_id):
        user = request.user
        booking = get_object_or_404(Booking, id=booking_id)

        if booking.user != user:
            return Response({"error": "Permission denied."}, status=403)

        deleted, _ = BookingSeat.objects.filter(
            booking=booking, seat_id=seat_id
        ).delete()
        if deleted == 0:
            return Response({"message": "Seat not in booking."}, status=200)

        self._notify_ws(booking.showtime.id, seat_id, user.id)
        return Response({"seat_removed": seat_id}, status=200)

    def _notify_ws(self, showtime_id, seat_id, sender_id):
        channel_layer = get_channel_layer()
        group_name = f"booking_{showtime_id}"
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "seat_removed",
                "message": {
                    "seat_id": seat_id,
                    "sender_id": sender_id,  # Thêm ID của người gửi để xử lý sau
                },
            },
        )


@extend_schema(tags=["Bookings"])
class ZaloPayPaymentView(APIView):
    def post(self, request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id)
        app_trans_id = time.strftime("%y%m%d") + "_" + str(int(time.time()))
        result = create_zalopay_payment(
            booking.id, int(booking.total_amount), app_trans_id=app_trans_id
        )

        logger.info("ZaloPay result:", result)
        if result.get("return_code") == 1:
            booking.app_trans_id = app_trans_id
            booking.save(update_fields=["app_trans_id"])

            return Response(
                {
                    "order_url": result["order_url"],
                    "zp_trans_token": result["zp_trans_token"],
                }
            )
        return Response(
            {"error": result.get("return_message", "ZaloPay error")},
            status=status.HTTP_400_BAD_REQUEST,
        )


@method_decorator(csrf_exempt, name="dispatch")
class ZaloPayCallbackView(APIView):
    def post(self, request):
        try:
            data = json.loads(request.body)
            logger.info("ZaloPay callback data:", data)

            # Verify callback signature
            callback_data = data["data"]
            received_mac = data["mac"]

            key1 = settings.ZALOPAY_KEY1
            raw_data = callback_data
            hash_data = hmac.new(
                key1.encode(), raw_data.encode(), hashlib.sha256
            ).hexdigest()

            if hash_data != received_mac:
                return HttpResponseBadRequest("Invalid MAC")

            callback_json = json.loads(callback_data)
            app_trans_id = callback_json.get("app_trans_id")
            # TODO: Kiểm tra trạng thái thanh toán khi deploy
            try:
                booking = get_object_or_404(Booking, app_trans_id=app_trans_id)
                if booking.status != "pending":
                    booking.status = "paid"  # cập nhật trạng thái
                    booking.save()
                return JsonResponse({"return_code": 1, "return_message": "Success"})
            except Booking.DoesNotExist:
                return JsonResponse(
                    {"return_code": 2, "return_message": "Booking not found"}
                )

        except Exception as e:
            logger.error("ZaloPay callback error:", str(e))
            return JsonResponse({"return_code": 3, "return_message": "Server error"})


@extend_schema(tags=["Bookings"])
class ZaloPayCheckStatusView(APIView):
    def get(self, request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id)

        app_trans_id = booking.app_trans_id  # bạn cần lưu app_trans_id khi tạo đơn
        url = "https://sb-openapi.zalopay.vn/v2/query"  # TODO: Chuyển sang URL chính thức khi deploy
        payload = {"app_id": settings.ZALOPAY_APP_ID, "app_trans_id": app_trans_id}

        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        response = requests.post(url, data=payload, headers=headers)
        result = response.json()

        if result.get("return_code") == 1:
            # Có thể cập nhật trạng thái booking nếu cần
            return Response(
                {
                    "status": result["status"],  # 1 là đã thanh toán
                    "message": result["return_message"],
                    "amount": result["amount"],
                    "zp_trans_id": result["zp_trans_id"],
                }
            )
        return Response(
            {"error": result.get("return_message", "Cannot check status")},
            status=status.HTTP_400_BAD_REQUEST,
        )


@extend_schema(tags=["Users"])
class UserPendingBookingView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        now = timezone.now()
        booking = (
            Booking.objects.filter(
                user=request.user, status="pending", expired_at__gt=now
            )
            .order_by("-booking_time")
            .first()
        )
        if not booking:
            return Response(
                {"detail": "No pending booking found or all expired."}, status=404
            )

        # Lấy tất cả ghế của booking
        booking_seats = BookingSeat.objects.filter(booking=booking).select_related(
            "seat__seat_type"
        )

        # Tính tổng extra_price từ seat types
        total_amount = Decimal("0.00")
        for bs in booking_seats:
            seat_type = bs.seat.seat_type
            if seat_type and seat_type.extra_price:
                # Tiền vé + tiền ghế
                price_per_seat = booking.showtime.price + seat_type.extra_price
                total_amount += price_per_seat

        # Cập nhật total_amount vào booking (nếu muốn lưu lại)
        booking.total_amount = total_amount
        booking.save(update_fields=["total_amount"])
        serializer = BookingDetailSerializer(booking)
        return Response(serializer.data)


from ..utils.send_mail import send_templated_email


class TestSendMailView(APIView):
    def get(self, request):
        subject = "Test Email Subject"
        to_email = "thliem143@gmail.com"
        context = {"confirmation_link": "https://example.com/confirm?token"}
        template_name = "emails/ticket_email.html"

        if not subject or not to_email:
            return Response(
                {"error": "Missing subject or to_email"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        send_templated_email(
            subject=subject,
            to_email=to_email,
            template_name=template_name,
            context=context,
        )
        return Response(
            {"message": "Email sent successfully!"}, status=status.HTTP_200_OK
        )
        
