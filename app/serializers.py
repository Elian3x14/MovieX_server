from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db import transaction
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.conf import settings
from django.core.mail import send_mail

from .models import Movie, Showtime, Seat, Booking, BookingSeat, SeatType, Cinema, Room


User = get_user_model()


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = User.EMAIL_FIELD

    def validate(self, attrs):
        # Map 'email' vào 'username' để tương thích với backend
        attrs["username"] = attrs.get("email")
        return super().validate(attrs)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "role"]


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True, validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "phone_number",
            "email",
            "password",
        ]

    def create(self, validated_data):
        user = User.objects.create_user(
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            phone_number=validated_data["phone_number"],
            email=validated_data["email"],
            username=validated_data["email"],  # Sử dụng email làm username
            password=validated_data["password"],
            role="user",  # Mặc định role là 'user'
            is_active=False,  # Tài khoản chưa kích hoạt
        )
        # Tạo token xác thực
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        activation_link = f"{settings.FRONTEND_URL}/activate/{uid}/{token}/"

        # Gửi mail
        send_mail(
            "Kích hoạt tài khoản",
            f"Chào {user.username}, hãy nhấp vào liên kết sau để kích hoạt tài khoản:\n{activation_link}",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Mật khẩu phải dài ít nhất 8 ký tự.")
        return value


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField()

    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Mật khẩu phải dài ít nhất 8 ký tự.")
        return value


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = "__all__"


class CinemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cinema
        fields = ["id", "name", "address", "city"]


class RoomSerializer(serializers.ModelSerializer):
    cinema = CinemaSerializer(read_only=True)

    class Meta:
        model = Room
        fields = ["id", "cinema", "name", "total_seats"]


class ShowtimeSerializer(serializers.ModelSerializer):
    movie = MovieSerializer(read_only=True)

    class Meta:
        model = Showtime
        fields = "__all__"


class SeatTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeatType
        fields = "__all__"


class SeatSerializer(serializers.ModelSerializer):
    seat_type = SeatTypeSerializer(read_only=True)

    class Meta:
        model = Seat
        fields = "__all__"


class BookingSeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingSeat
        fields = ["seat_id"]


class BookingSerializer(serializers.ModelSerializer):
    seats = BookingSeatSerializer(many=True)
    showtime = serializers.PrimaryKeyRelatedField(
        queryset=Showtime.objects.all(), write_only=True
    )

    class Meta:
        model = Booking
        fields = ["showtime", "total_amount", "seats"]

    def create(self, validated_data):
        seats_data = validated_data.pop("seats")
        user = self.context["request"].user
        showtime = validated_data["showtime"]
        total = 0

        with transaction.atomic():
            # Tính tổng tiền
            for seat_data in seats_data:
                seat = Seat.objects.get(id=seat_data["seat_id"])
                extra = seat.seat_type.extra_price if seat.seat_type else 0
                total += showtime.price + extra

            validated_data["total_amount"] = total
            booking = Booking.objects.create(user=user, **validated_data)

            for seat_data in seats_data:
                BookingSeat.objects.create(
                    booking=booking, seat_id=seat_data["seat_id"]
                )

        return booking

    def update(self, instance, validated_data):
        if instance.status in ["paid", "cancelled"]:
            raise ValidationError("Cannot modify a paid or cancelled booking.")

        seats_data = validated_data.pop("seats", None)
        showtime = validated_data.get("showtime", instance.showtime)

        with transaction.atomic():
            for attr, value in validated_data.items():
                setattr(instance, attr, value)

            if seats_data is not None:
                # Xoá ghế cũ
                BookingSeat.objects.filter(booking=instance).delete()

                total = 0
                for seat_data in seats_data:
                    seat = Seat.objects.get(id=seat_data["seat_id"])
                    BookingSeat.objects.create(booking=instance, seat=seat)
                    extra = seat.seat_type.extra_price if seat.seat_type else 0
                    total += showtime.price + extra

                instance.total_amount = total

            instance.save()
        return instance


class BookingSeatSerializer(serializers.ModelSerializer):
    seat = SeatSerializer(read_only=True)

    class Meta:
        model = BookingSeat
        fields = ["id", "booking", "seat"]
