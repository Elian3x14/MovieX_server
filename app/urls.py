from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'rooms', RoomViewSet, basename='room')
router.register(r'booking-seats', BookingSeatViewSet, basename='booking-seat')

urlpatterns = [
    path("movies/", MovieListView.as_view()),
    path("movies/create/", MovieCreateView.as_view()),
    path("movies/<int:pk>/", MovieDetailView.as_view()),
    path("movies/<int:movie_id>/showtimes/", ShowtimeListView.as_view()),
    # 
    path('cinemas/', CinemaListCreateView.as_view(), name='cinema-list-create'),
    path('cinemas/<int:pk>/', CinemaRetrieveUpdateDestroyView.as_view(), name='cinema-detail'),
    #
    path("showtimes/create/", ShowtimeCreateView.as_view()),
    path("showtimes/<int:pk>/", ShowtimeDetailView.as_view()),
    path("showtimes/<int:showtime_id>/seats/", AvailableSeatsView.as_view()),
    #
    path("seat-types/", SeatTypeListCreateView.as_view(), name="seat-type-list-create"),
    path("seat-types/<int:pk>/", SeatTypeDetailView.as_view(), name="seat-type-detail"),
    #
    path("seats/create/", SeatCreateView.as_view()),
    path("seats/<int:pk>/", SeatDetailView.as_view()),
    #
    path("bookings/", BookingCreateView.as_view()),
    path("bookings/<int:pk>/", BookingDetailView.as_view()),
]

urlpatterns += router.urls
