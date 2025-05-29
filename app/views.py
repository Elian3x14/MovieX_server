from django.db.models import Q
from rest_framework.decorators import action
from rest_framework import generics, permissions, viewsets
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.http import urlsafe_base64_decode
from drf_spectacular.utils import OpenApiParameter
from django.contrib.auth.tokens import default_token_generator
from rest_framework import status
from django.http import HttpResponseRedirect
from rest_framework.permissions import (
    BasePermission,
    IsAuthenticatedOrReadOnly,
    SAFE_METHODS,
)
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from decimal import Decimal


from drf_spectacular.utils import extend_schema
from django.conf import settings

from .models import *
from .serializers import *
from django.core.mail import send_mail


class IsAdminOrReadOnly(BasePermission):
    """
    Cho phép mọi người dùng GET, HEAD, OPTIONS.
    Nhưng chỉ admin mới được POST, PUT, DELETE.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class IsAuthorOrAdmin(BasePermission):
    """
    - GET: Ai cũng được
    - POST/PUT/DELETE: Chỉ người đăng nhập
    - PUT/DELETE: Chỉ author hoặc admin
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.author == request.user or request.user.is_staff


class MovieReviewPagination(PageNumberPagination):
    page_size = 1  # số review mỗi trang
    page_size_query_param = "page_size"
    max_page_size = 100


@extend_schema(tags=["Auth"])
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        # Truyền request vào context để sử dụng trong serializer
        serializer.save(request=self.request)


@extend_schema(tags=["Auth"])
class ActivateUserView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        parameters=[
            OpenApiParameter(name="uidb64", type=str, location=OpenApiParameter.PATH),
            OpenApiParameter(name="token", type=str, location=OpenApiParameter.PATH),
        ]
    )
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            return Response({"error": "Liên kết không hợp lệ."}, status=400)

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            # Redirect đến trang xác thực thành công ở client
            return HttpResponseRedirect(
                f"http://{settings.FRONTEND_URL}/activate-success"
            )
        else:
            return Response({"error": "Token không hợp lệ."}, status=400)


@extend_schema(tags=["Auth"])
class EmailLoginView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer


@extend_schema(tags=["Auth"])
class UserView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


@extend_schema(tags=["Auth"])
class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=ChangePasswordSerializer, responses={200: dict, 400: dict})
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            old_password = serializer.validated_data["old_password"]
            new_password = serializer.validated_data["new_password"]

            if not user.check_password(old_password):
                return Response(
                    {"error": "Mật khẩu cũ không đúng."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user.set_password(new_password)
            user.save()
            return Response(
                {"success": "Mật khẩu đã được thay đổi."}, status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["Auth"])
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=None, responses={204: None})
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Logged out successfully"}, status=200)
        except Exception as e:
            return Response({"detail": str(e)}, status=400)


@extend_schema(tags=["Auth"])
class PasswordResetRequestView(APIView):
    @extend_schema(
        request=PasswordResetRequestSerializer, responses={200: dict, 404: dict}
    )
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "Email không tồn tại."}, status=404)

        token = default_token_generator.make_token(user)

        # Đường dẫn giả định để người dùng reset
        reset_url = f"http://localhost:8000/api/reset-password/?token={token}&email={user.email}"

        # Gửi mail giả (log vào console)
        send_mail(
            subject="Đặt lại mật khẩu",
            message=f"Nhấn vào link sau để đặt lại mật khẩu: {reset_url}",
            from_email="noreply@example.com",
            recipient_list=[user.email],
            fail_silently=False,
        )

        return Response({"detail": "Đã gửi mail xác thực đặt lại mật khẩu."})


@extend_schema(tags=["Auth"])
class PasswordResetConfirmView(APIView):

    @extend_schema(
        request=PasswordResetConfirmSerializer, responses={200: dict, 400: dict}
    )
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password"]
        email = request.query_params.get("email")

        if not email:
            return Response({"detail": "Thiếu email."}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "Người dùng không tồn tại."}, status=404)

        if not default_token_generator.check_token(user, token):
            return Response({"detail": "Token không hợp lệ."}, status=400)

        user.set_password(new_password)
        user.save()
        return Response({"detail": "Mật khẩu đã được đặt lại thành công."})


@extend_schema(tags=["Actors"])
class ActorViewSet(viewsets.ModelViewSet):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer
    permission_classes = [IsAdminOrReadOnly]


@extend_schema(tags=["Genres"])
class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrReadOnly]


@extend_schema(tags=["Movies"])
class MovieListView(generics.ListAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [permissions.AllowAny]  # Không cần đăng nhập


@extend_schema(tags=["Movies"])
class MovieDetailView(generics.RetrieveAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [permissions.AllowAny]  # Không cần đăng nhập
    lookup_field = "id"  # Mặc định là 'pk', bạn dùng 'id' nếu muốn rõ ràng hơn


@extend_schema(tags=["Movies"])
class MovieCreateView(generics.CreateAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [permissions.IsAdminUser]


@extend_schema(tags=["Movies"])
class MovieUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [permissions.IsAdminUser]


@extend_schema(tags=["Cinemas"])
class CinemaListCreateView(generics.ListCreateAPIView):
    queryset = Cinema.objects.all()
    serializer_class = CinemaSerializer


@extend_schema(tags=["Cinemas"])
class CinemaRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Cinema.objects.all()
    serializer_class = CinemaSerializer


@extend_schema(tags=["Rooms"])  # Gắn tag cho tài liệu API
class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer


@extend_schema(tags=["Movies"])
class ShowtimeListView(generics.ListAPIView):
    serializer_class = ShowtimeSerializer

    def get_queryset(self):
        movie_id = self.kwargs["movie_id"]
        return Showtime.objects.filter(movie_id=movie_id)


@extend_schema(tags=["Showtimes"])
class ShowtimeCreateView(generics.CreateAPIView):
    queryset = Showtime.objects.all()
    serializer_class = ShowtimeSerializer
    # permission_classes = [permissions.IsAdminUser]


@extend_schema(tags=["Showtimes"])
class AvailableSeatsView(generics.ListAPIView):
    serializer_class = SeatSerializer

    def get_queryset(self):
        showtime_id = self.kwargs["showtime_id"]

        try:
            showtime = Showtime.objects.select_related("room").get(id=showtime_id)
        except Showtime.DoesNotExist:
            return Seat.objects.none()

        room = showtime.room

        # Ghế đã được đặt
        reserved_seat_ids = set(
            BookingSeat.objects.filter(
                booking__showtime_id=showtime_id,
                booking__status="paid",
            ).values_list("seat_id", flat=True)
        )
        # Ghế đã được giữ
        held_seat_ids = set(
            BookingSeat.objects.filter(
                booking__showtime_id=showtime_id,
                booking__status="pending",
            ).values_list("seat_id", flat=True)
        )

        # Toàn bộ ghế trong phòng
        all_seats = Seat.objects.filter(room=room)

        # Cập nhật trạng thái ghế
        for seat in all_seats:
            if seat.id in held_seat_ids:
                seat.status = "hold"
            elif seat.id in reserved_seat_ids:
                seat.status = "reserved"
            else:
                seat.status = "available"

        return all_seats


@extend_schema(tags=["Showtimes"])
class ShowtimeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Showtime.objects.all()
    serializer_class = ShowtimeSerializer
    # permission_classes = [permissions.IsAdminUser]


@extend_schema(tags=["SeatTypes"])
class SeatTypeListCreateView(generics.ListCreateAPIView):
    queryset = SeatType.objects.all()
    serializer_class = SeatTypeSerializer


@extend_schema(tags=["SeatTypes"])
class SeatTypeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SeatType.objects.all()
    serializer_class = SeatTypeSerializer


@extend_schema(tags=["Seats"])
class SeatCreateView(generics.CreateAPIView):
    queryset = Seat.objects.all()
    serializer_class = SeatSerializer
    # permission_classes = [permissions.IsAdminUser]


@extend_schema(tags=["Seats"])
class SeatDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Seat.objects.all()
    serializer_class = SeatSerializer
    # permission_classes = [permissions.IsAdminUser]

@extend_schema(tags=["Bookings"])
class BookingCreateView(generics.CreateAPIView):
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
            expired_at__gt=timezone.now()
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
    # permission_classes = [permissions.IsAuthenticated]


@extend_schema(tags=["BookingSeats"])
class BookingSeatViewSet(viewsets.ModelViewSet):
    queryset = BookingSeat.objects.all()
    serializer_class = BookingSeatSerializer

    @action(detail=True, methods=["get"], url_path="seats")
    def seats_by_booking(self, request, pk=None):
        # pk là ID của booking (ở đây tương ứng với booking_id)
        booking_id = pk
        # Lấy booking, kiểm tra quyền
        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return Response({"detail": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)

        if booking.user != request.user:
            return Response({"detail": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

        # Lấy seat list của booking
        booking_seats = BookingSeat.objects.filter(booking=booking)
        seats = [bs.seat for bs in booking_seats]

        serializer = SeatSerializer(seats, many=True)
        return Response(serializer.data)

@extend_schema(tags=["Reviews"])
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsAuthorOrAdmin,
    ]  # Ai cũng xem được, nhưng chỉ người tạo hoặc admin mới sửa/xóa được

    def perform_create(self, serializer):
        # Tự động gán author là user đang đăng nhập
        serializer.save(author=self.request.user)


@extend_schema(
    tags=["Movies"],
)
class MovieReviewList(generics.ListAPIView):
    serializer_class = ReviewSerializer
    pagination_class = MovieReviewPagination
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        movie_id = self.kwargs["movie_id"]
        return Review.objects.filter(movie_id=movie_id).order_by("-date")


@extend_schema(tags=["Bookings"])
class AddBookingSeatView(APIView):
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
        if BookingSeat.objects.filter(
            seat=seat, booking__showtime=booking.showtime
        ).filter(
            Q(booking__status="paid") |
            Q(booking__status="pending", booking__expired_at__gt=now)
        ).exists():
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
class RemoveBookingSeatView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, booking_id, seat_id):
        user = request.user
        booking = get_object_or_404(Booking, id=booking_id)

        if booking.user != user:
            return Response({"error": "Permission denied."}, status=403)

        deleted, _ = BookingSeat.objects.filter(booking=booking, seat_id=seat_id).delete()
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

@extend_schema(tags=["Users"])
class UserPendingBookingView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        now = timezone.now()
        booking = (
            Booking.objects
            .filter(user=request.user, status='pending', expired_at__gt=now)
            .order_by('-booking_time')
            .first()
        )
        if not booking:
            return Response({"detail": "No pending booking found or all expired."}, status=404)
        
        # Lấy tất cả ghế của booking
        booking_seats = BookingSeat.objects.filter(booking=booking).select_related('seat__seat_type')

        # Tính tổng extra_price từ seat types
        total_amount = Decimal('0.00')
        for bs in booking_seats:
            seat_type = bs.seat.seat_type
            if seat_type and seat_type.extra_price:
                # Tiền vé + tiền ghế
                price_per_seat = booking.showtime.price + seat_type.extra_price 
                total_amount += price_per_seat

        # Cập nhật total_amount vào booking (nếu muốn lưu lại)
        booking.total_amount = total_amount
        booking.save(update_fields=['total_amount'])
        serializer = BookingDetailSerializer(booking)
        return Response(serializer.data)