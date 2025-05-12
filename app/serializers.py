from rest_framework import serializers
from .models import Movie, Showtime, Seat, Booking, BookingSeat, SeatType, Cinema, Room
from rest_framework.exceptions import ValidationError
from django.db import transaction


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
    seats = BookingSeatSerializer(many=True, write_only=True)

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
        fields = ['id', 'booking', 'seat']

