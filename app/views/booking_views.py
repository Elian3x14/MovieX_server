from rest_framework import generics, status
from drf_spectacular.utils import extend_schema
from rest_framework import permissions
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
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
import hmac
import hashlib
import time
from django.conf import settings
from decimal import Decimal


from ..serializers import BookingSerializer, BookingDetailSerializer
from ..models import Booking, Showtime, BookingSeat, Seat
from ..payments import create_zalopay_payment


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
        print(f"send to group name: {group_name}")
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

        print("ZaloPay result:", result)
        if result.get("return_code") == 1:
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


@csrf_exempt
def zalopay_callback(request):
    if request.method == "POST":
        data = json.loads(request.body)
        received_mac = data.get("mac")
        callback_data = data.get("data")

        # Tính toán lại MAC để xác thực
        key2 = settings.ZALOPAY_KEY2
        calculated_mac = hmac.new(
            key2.encode(), callback_data.encode(), hashlib.sha256
        ).hexdigest()

        if hmac.compare_digest(received_mac, calculated_mac):
            # Xử lý dữ liệu callback hợp lệ
            callback_json = json.loads(callback_data)
            app_trans_id = callback_json.get("app_trans_id")
            # Cập nhật trạng thái đơn hàng trong cơ sở dữ liệu
            return JsonResponse({"return_code": 1, "return_message": "success"})
        else:
            return JsonResponse({"return_code": -1, "return_message": "invalid mac"})
    return JsonResponse({"return_code": -1, "return_message": "invalid request"})


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
