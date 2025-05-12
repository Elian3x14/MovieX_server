from django.db.models import Q

from rest_framework import generics, permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from rest_framework import status

from drf_spectacular.utils import extend_schema

from .models import (
    Movie,
    Showtime,
    Seat,
    BookingSeat,
    Booking,
    SeatType,
    Cinema,
    Room,
    User,
)
from .serializers import (
    MovieSerializer,
    ShowtimeSerializer,
    SeatSerializer,
    BookingSerializer,
    SeatTypeSerializer,
    CinemaSerializer,
    RoomSerializer,
    BookingSeatSerializer,
    RegisterSerializer,
    UserSerializer,
    EmailTokenObtainPairSerializer,
    ChangePasswordSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)
from django.core.mail import send_mail


@extend_schema(tags=["Auth"])
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


@extend_schema(tags=["Auth"])
class ActivateUserView(APIView):
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            return Response({"error": "Liên kết không hợp lệ."}, status=400)

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({"message": "Tài khoản đã được kích hoạt."}, status=200)
        else:
            return Response({"error": "Token không hợp lệ."}, status=400)


@extend_schema(tags=["Auth"])
class EmailLoginView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer


@extend_schema(tags=["Auth"])
class UserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

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


@extend_schema(tags=["Movies"])
class MovieListView(generics.ListAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer


@extend_schema(tags=["Movies"])
class MovieCreateView(generics.CreateAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    # permission_classes = [permissions.IsAdminUser]  # chỉ admin được tạo


@extend_schema(tags=["Movies"])
class MovieDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    # permission_classes = [permissions.IsAdminUser]


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


@extend_schema(tags=["Showtimes"])
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
class AvailableSeatsView(generics.ListAPIView):
    serializer_class = SeatSerializer

    def get_queryset(self):
        showtime_id = self.kwargs["showtime_id"]
        booked_seat_ids = BookingSeat.objects.filter(
            booking__showtime_id=showtime_id, booking__status__in=["pending", "paid"]
        ).values_list("seat_id", flat=True)

        return Seat.objects.exclude(id__in=booked_seat_ids)


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
    # permission_classes = [permissions.IsAuthenticated]


@extend_schema(tags=["Bookings"])
class BookingDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    # permission_classes = [permissions.IsAuthenticated]


@extend_schema(tags=["BookingSeats"])
class BookingSeatViewSet(viewsets.ModelViewSet):
    queryset = BookingSeat.objects.all()
    serializer_class = BookingSeatSerializer
