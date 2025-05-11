from rest_framework import generics, permissions
from .models import Movie, Showtime, Seat, BookingSeat
from .serializers import MovieSerializer, ShowtimeSerializer, SeatSerializer, BookingSerializer
from rest_framework.response import Response
from django.db.models import Q


class MovieListView(generics.ListAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer


class ShowtimeListView(generics.ListAPIView):
    serializer_class = ShowtimeSerializer

    def get_queryset(self):
        movie_id = self.kwargs['movie_id']
        return Showtime.objects.filter(movie_id=movie_id)


class AvailableSeatsView(generics.ListAPIView):
    serializer_class = SeatSerializer

    def get_queryset(self):
        showtime_id = self.kwargs['showtime_id']
        booked_seat_ids = BookingSeat.objects.filter(
            booking__showtime_id=showtime_id,
            booking__status__in=['pending', 'paid']
        ).values_list('seat_id', flat=True)

        return Seat.objects.exclude(id__in=booked_seat_ids)


class BookingCreateView(generics.CreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
