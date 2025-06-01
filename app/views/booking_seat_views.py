
from rest_framework import viewsets, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action

from ..serializers import BookingSeatSerializer, SeatSerializer
from ..models import BookingSeat, Booking

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
            return Response(
                {"detail": "Booking not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if booking.user != request.user:
            return Response(
                {"detail": "Permission denied"}, status=status.HTTP_403_FORBIDDEN
            )

        # Lấy seat list của booking
        booking_seats = BookingSeat.objects.filter(booking=booking)
        seats = [bs.seat for bs in booking_seats]

        serializer = SeatSerializer(seats, many=True)
        return Response(serializer.data)
