from django.urls import path
from .views import MovieListView, ShowtimeListView, AvailableSeatsView, BookingCreateView

urlpatterns = [
    path('movies/', MovieListView.as_view(), name='movie-list'),
    path('movies/<int:movie_id>/showtimes/', ShowtimeListView.as_view(), name='movie-showtimes'),
    path('showtimes/<int:showtime_id>/available-seats/', AvailableSeatsView.as_view(), name='available-seats'),
    path('bookings/', BookingCreateView.as_view(), name='create-booking'),
]
