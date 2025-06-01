from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions

from django.utils import timezone

from ..serializers import ShowtimeSerializer, SeatSerializer
from ..models import Showtime, Seat, BookingSeat



@extend_schema(tags=["Showtimes"])
class ShowtimeCreateView(generics.CreateAPIView):
    queryset = Showtime.objects.all()
    serializer_class = ShowtimeSerializer
    # permission_classes = [permissions.IsAdminUser]


@extend_schema(tags=["Showtimes"])
class AvailableSeatsView(generics.ListAPIView):
    serializer_class = SeatSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        showtime_id = self.kwargs["showtime_id"]
        user = self.request.user

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

        # Ghế đang giữ bởi tất cả người dùng
        all_held_seats = BookingSeat.objects.filter(
            booking__showtime_id=showtime_id,
            booking__status="pending",
            booking__expired_at__gt=timezone.now(),
        ).select_related("booking", "seat")

        # Ghế được giữ bởi user hiện tại
        user_held_seat_ids = set(
            bs.seat_id for bs in all_held_seats if bs.booking.user_id == user.id
        )

        # Ghế được giữ bởi người khác
        other_held_seat_ids = set(
            bs.seat_id for bs in all_held_seats if bs.booking.user_id != user.id
        )

        # Toàn bộ ghế trong phòng
        all_seats = Seat.objects.filter(room=room)

        # Gán trạng thái cho từng ghế
        for seat in all_seats:
            if seat.id in reserved_seat_ids:
                seat.status = "reserved"
            elif seat.id in user_held_seat_ids:
                seat.status = "selected"  # Ghế do chính user giữ
            elif seat.id in other_held_seat_ids:
                seat.status = "hold"  # Ghế do người khác giữ
            else:
                seat.status = "available"

        return all_seats


@extend_schema(tags=["Showtimes"])
class ShowtimeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Showtime.objects.all()
    serializer_class = ShowtimeSerializer
    # permission_classes = [permissions.IsAdminUser]