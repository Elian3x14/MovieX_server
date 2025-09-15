from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import *

router = DefaultRouter()
router.register(r"rooms", RoomViewSet, basename="room")
router.register(r"booking-seats", BookingSeatViewSet, basename="booking-seat")
router.register(r"actors", ActorViewSet)
router.register(r"genres", GenreViewSet)
router.register(r"reviews", ReviewViewSet, basename="review")
router.register(r"movies", MovieViewSet, basename="movie")
router.register(r"cinemas", CinemaViewSet, basename="cinema")

urlpatterns = [
    # auth
    path("register/", RegisterView.as_view(), name="register"),
    path("activate/<uidb64>/<token>/", ActivateUserView.as_view(), name="activate"),
    path("login/", EmailLoginView.as_view(), name="token_obtain_pair"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", UserView.as_view(), name="user-info"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("password-reset/", PasswordResetRequestView.as_view()),
    path("password-reset-confirm/", PasswordResetConfirmView.as_view()),
    #
    path("movies/<int:movie_id>/showtimes/", ShowtimeListView.as_view()),
    path(
        "movies/<int:movie_id>/reviews/",
        MovieReviewList.as_view(),
        name="movie-reviews",
    ),
    path("rooms/<int:room_id>/seats/", SeatByRoomView.as_view(), name="room-seat-list"),
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
    path("bookings/", BookingGetOrCreateView.as_view()),
    path("bookings/<int:pk>/", BookingDetailView.as_view()),
    path(
        "bookings/<int:booking_id>/add-seat/<int:seat_id>/",
        AddBookingSeatView.as_view(),
    ),
    path(
        "bookings/<int:booking_id>/remove-seat/<int:seat_id>/",
        RemoveBookingSeatView.as_view(),
    ),
    # User-specific bookings
    path(
        "users/bookings/pending/",
        UserPendingBookingView.as_view(),
        name="user-pending-bookings",
    ),
    # payment
    path(
        "bookings/<int:booking_id>/pay/zalo-pay/",
        ZaloPayPaymentView.as_view(),
        name="zalo-payment",
    ),
    path(
        "bookings/<int:booking_id>/pay/zalo-pay/status",
        ZaloPayCheckStatusView.as_view(),
        name="zalo-payment-status",
    ),
    path(
        "payment/zalo_pay/callback/",
        ZaloPayCallbackView.as_view(),
        name="zalo-pay-callback",
    ),
    # test
    path("test-send-mail/", TestSendMailView.as_view(), name="test-send-mail"),
]

urlpatterns += router.urls
