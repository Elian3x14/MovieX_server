from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.utils.translation import gettext_lazy as _

# Regex cho số điện thoại Việt Nam: 10 số, bắt đầu bằng 03, 05, 07, 08, 09
vietnam_phone_regex = RegexValidator(
    regex=r"^(03|05|07|08|09)\d{8}$",
    message="Số điện thoại không hợp lệ. Vui lòng nhập số 10 chữ số bắt đầu bằng 03, 05, 07, 08, hoặc 09.",
)


class User(AbstractUser):
    ROLE_CHOICES = (("user", "User"), ("admin", "Admin"))
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="user")
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    phone_number = models.CharField(
        max_length=10,
        unique=True,
        validators=[vietnam_phone_regex],
        verbose_name=_("phone number"),
    )

    email = models.EmailField(unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "username",
    ]

    def __str__(self):
        return self.email


class Genre(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Actor(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Movie(models.Model):
    NOW_SHOWING = "now-showing"
    COMING_SOON = "coming-soon"
    RELEASE_STATUS_CHOICES = [
        (NOW_SHOWING, "Now Showing"),
        (COMING_SOON, "Coming Soon"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    poster_url = models.URLField(blank=False)
    trailer_url = models.URLField(blank=True)
    backdrop_url = models.URLField(blank=True)
    genres = models.ManyToManyField(Genre, related_name="movies")
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
    )
    duration = models.PositiveIntegerField()  # in minutes
    year = models.PositiveIntegerField()  # in YYYY format
    director = models.CharField(max_length=100)
    actors = models.ManyToManyField(Actor, related_name="movies")
    release_date = models.DateField()
    release_status = models.CharField(
        max_length=20,
        choices=RELEASE_STATUS_CHOICES,
        default=COMING_SOON,
    )

    def __str__(self):
        return self.title


class Cinema(models.Model):
    name = models.CharField(max_length=100)

    # Tách địa chỉ
    street = models.CharField(max_length=200, default="")
    ward = models.CharField(max_length=100, blank=True, null=True, default="")
    district = models.CharField(max_length=100, blank=True, null=True, default="")
    city = models.CharField(max_length=100, blank=True, null=True, default="")

    def __str__(self):
        return self.name

    @property
    def full_address(self):
        parts = [self.street, self.ward, self.district, self.city]
        return ", ".join(part for part in parts if part)

    @property
    def number_of_rooms(self):
        return self.rooms.count()  # Nếu liên kết là related_name="rooms"


class Room(models.Model):
    cinema = models.ForeignKey(Cinema, on_delete=models.CASCADE, related_name="rooms")
    name = models.CharField(max_length=50)
    no_row = models.PositiveIntegerField(default=1)  # số hàng
    no_column = models.PositiveIntegerField(default=1)  # số cột

    def create_seats(self):
        """
        Tự động tạo ghế cho phòng chiếu theo số hàng/cột.
        """

        for i in range(self.no_row):
            row_label = chr(ord("A") + i)  # A, B, C,...
            for col in range(1, self.no_column + 1):
                Seat.objects.create(room=self, seat_row=row_label, seat_col=col)

    def __str__(self):
        return f"{self.name} - {self.cinema.name}"


class SeatType(models.Model):
    name = models.CharField(max_length=50)  # VD: VIP, Standard, Couple
    def __str__(self):
        return self.name


class Seat(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    seat_row = models.CharField(max_length=1)
    seat_col = models.IntegerField()
    seat_type = models.ForeignKey(
        SeatType, on_delete=models.SET_NULL, null=True, blank=True
    )
    is_maintenance = models.BooleanField(default=False)

    class Meta:
        unique_together = ("room", "seat_row", "seat_col")

    def __str__(self):
        return f"{self.room.name} - Row: {self.seat_row}, Col: {self.seat_col}"


class SeatPrice(models.Model):
    showtime = models.ForeignKey(
        "Showtime", on_delete=models.CASCADE, related_name="seat_prices"
    )
    seat_type = models.ForeignKey(SeatType, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ("showtime", "seat_type")

    def __str__(self):
        return f"{self.seat_type.name} - {self.showtime} - {self.price}"


class Showtime(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.movie.title} - {self.room.name} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"


class Booking(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("expired", "Expired"),
        ("cancelled", "Cancelled"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    showtime = models.ForeignKey(Showtime, on_delete=models.CASCADE)
    booking_time = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    expired_at = models.DateTimeField(null=True, blank=True)
    app_trans_id = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return f"Booking {self.id} - {self.user.email} - {self.showtime.movie.title} - {self.booking_time.strftime('%Y-%m-%d %H:%M')}"


class BookingSeat(models.Model):
    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name="booking_seats"
    )
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    final_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    class Meta:
        unique_together = ("booking", "seat")

    def __str__(self):
        return f"BookingSeat {self.id} - Booking: {self.booking.id} - Seat: {self.seat.room.name} - Row: {self.seat.seat_row}, Col: {self.seat.seat_col}"


class Payment(models.Model):
    class PaymentMethod(models.TextChoices):
        CREDIT_DEBIT = "credit_debit", "Credit/Debit Card"
        E_WALLET = "e_wallet", "E-Wallet"
        INTERNET_BANKING = "internet_banking", "Internet Banking"

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CREDIT_DEBIT,
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.id} - Booking: {self.booking.id} - Amount: {self.amount} - Method: {self.get_method_display()}"


class Review(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="reviews")
    rating = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        default=0,
    )
    comment = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author} - {self.rating}"
