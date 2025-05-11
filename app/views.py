from rest_framework import generics, permissions
from .models import Movie, Showtime, Seat, BookingSeat, Booking, SeatType
from .serializers import (
    MovieSerializer,
    ShowtimeSerializer,
    SeatSerializer,
    BookingSerializer,
    SeatTypeSerializer,
)
from rest_framework.response import Response
from django.db.models import Q
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets


@extend_schema(tags=["Movies"])
class MovieListView(generics.ListAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer


@extend_schema(tags=["Movies"])
class MovieCreateView(generics.CreateAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [permissions.IsAdminUser]  # chỉ admin được tạo


@extend_schema(tags=["Movies"])
class MovieDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [permissions.IsAdminUser]


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


class SeatTypeListCreateView(generics.ListCreateAPIView):
    queryset = SeatType.objects.all()
    serializer_class = SeatTypeSerializer


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
    permission_classes = [permissions.IsAdminUser]


@extend_schema(tags=["Seats"])
class SeatDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Seat.objects.all()
    serializer_class = SeatSerializer
    permission_classes = [permissions.IsAdminUser]


@extend_schema(tags=["Bookings"])
class BookingCreateView(generics.CreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]


@extend_schema(tags=["Bookings"])
class BookingDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
