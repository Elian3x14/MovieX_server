from rest_framework import serializers
from .models import Movie, Showtime, Seat, Booking, BookingSeat
from rest_framework.exceptions import ValidationError
from django.db import transaction


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'


class ShowtimeSerializer(serializers.ModelSerializer):
    movie = MovieSerializer(read_only=True)

    class Meta:
        model = Showtime
        fields = '__all__'


class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = '__all__'


class BookingSeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingSeat
        fields = ['seat_id']


class BookingSerializer(serializers.ModelSerializer):
    seats = BookingSeatSerializer(many=True, write_only=True)

    class Meta:
        model = Booking
        fields = ['showtime', 'total_amount', 'seats']

    def create(self, validated_data):
        seats_data = validated_data.pop('seats')
        user = self.context['request'].user
        booking = Booking.objects.create(user=user, **validated_data)

        for seat in seats_data:
            BookingSeat.objects.create(booking=booking, seat_id=seat['seat_id'])

        return booking

    def update(self, instance, validated_data):
        if instance.status in ['paid', 'cancelled']:
            raise ValidationError("Cannot modify a paid or cancelled booking.")

        seats = validated_data.pop('seats', None)

        with transaction.atomic():
            for attr, value in validated_data.items():
                setattr(instance, attr, value)

            if seats is not None:
                # Xoá ghế cũ
                BookingSeat.objects.filter(booking=instance).delete()
                # Tạo ghế mới
                for seat in seats:
                    BookingSeat.objects.create(booking=instance, seat=seat)

                # Cập nhật total_amount
                seat_count = len(seats)
                instance.total_amount = instance.showtime.price * seat_count

            instance.save()
        return instance

