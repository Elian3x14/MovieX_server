from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify

from .regexs import vietnam_phone_regex


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
        null=True,
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
    slug = models.SlugField(max_length=110, unique=True, blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Nếu chưa có slug hoặc tên thay đổi
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            # Đảm bảo slug là duy nhất
            while Genre.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)


class Actor(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=110, unique=True, blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            # Đảm bảo slug không trùng
            while Actor.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)


class Movie(models.Model):
    # Tiêu đề
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    # Hình ảnh poster
    poster_url = models.URLField(blank=False)
    # Video trailer
    trailer_url = models.URLField(blank=True)
    # Hình nền (backdrop)
    backdrop_url = models.URLField(blank=True)
    # Đánh giá phim (0.0 - 10.0)
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
    )
    duration = models.PositiveIntegerField()  # in minutes
    year = models.PositiveIntegerField()  # in YYYY format
    director = models.CharField(max_length=100)  # Đạo diễn phim

    genres = models.ManyToManyField(Genre, related_name="movies")
    actors = models.ManyToManyField(Actor, related_name="movies")

    release_date = models.DateField()  # Ngày phát hành phim
    # Tạo slug tự động từ tiêu đề
    slug = models.SlugField(max_length=210, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Movie.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Cinema(models.Model):
    # Tên rạp chiếu
    name = models.CharField(max_length=100)

    # Tách địa chỉ
    street = models.CharField(max_length=200, default="")
    ward = models.CharField(max_length=100, blank=True, null=True, default="")
    district = models.CharField(max_length=100, blank=True, null=True, default="")
    city = models.CharField(max_length=100, blank=True, null=True, default="")

    def __str__(self):
        return self.name

    @property
    def number_of_rooms(self):
        return self.rooms.count()  # Nếu liên kết là related_name="rooms"


class Room(models.Model):
    cinema = models.ForeignKey(Cinema, on_delete=models.CASCADE, related_name="rooms")
    # Tên phòng chiếu
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
    short_name = models.CharField(
        max_length=10, null=True, default=""
    )  # VD: VIP, STD, COUPLE
    color = models.CharField(max_length=7, default="#FFFFFF")  # Mã màu HEX cho ghế

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
    seat_type = models.ForeignKey(
        SeatType, on_delete=models.CASCADE, related_name="seat_prices"
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ("showtime", "seat_type")

    def __str__(self):
        return f"{self.seat_type.name} - {self.showtime} - {self.price}"


class Showtime(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="showtimes")
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="showtimes")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()  # Tính toán từ start_time và duration của movie

    def __str__(self):
        return f"{self.movie.title} - {self.room.name} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"


class BookingStatus(models.TextChoices):
    # Đang giữ ghế, khi người dùng đặt vé,
    # hệ thống sẽ giữ ghế trong một khoảng thời gian nhất định
    # tức là booking sẽ có trạng thái PENDING và phiên chưa hết hạn (expired_at > now)
    PENDING_TO_SELECT_SEAT = "pending_to_select_seat", "Pending to Select Seat"
    # Trạng thái khi người dùng đã đặt vé nhưng chưa thanh toán
    # và hệ thống đã giữ ghế trong một khoảng thời gian nhất định
    PENDING_TO_PAY = "pending_to_pay", "Pending to Pay"
    # Trạng thái khi người dùng đã thanh toán thành công
    # và hệ thống đã xác nhận thanh toán
    PAID = "paid", "Paid"
    # Trạng thái khi người dùng đã sử dụng vé (đã xem phim)
    USED = "used", "Used"
    # Trạng thái khi người dùng đã hủy vé đã đặt
    # và hệ thống đã hoàn tiền (nếu có)
    CANCELLED = "cancelled", "Cancelled"


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    showtime = models.ForeignKey(Showtime, on_delete=models.CASCADE)
    booking_time = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=32,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING_TO_SELECT_SEAT,
        verbose_name="Trạng thái đặt vé",
    )
    # Thời gian hết hạn để người dùng chọn ghế
    select_seat_expired_at = models.DateTimeField(null=True, blank=True)
    # Thời gian hết hạn để người dùng thanh toán
    pay_expired_at = models.DateTimeField(null=True, blank=True)
    app_trans_id = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return f"Booking {self.id} - {self.user.email} - {self.showtime.movie.title} - {self.booking_time.strftime('%Y-%m-%d %H:%M')}"


class BookingSeat(models.Model):
    """
    Chi tiết ghế được đặt trong một Booking
    Tương tự như OrderDetail (n-1) Order trong thương mại điện tử
    """

    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name="booking_seats"
    )
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    # giá đã chốt, tính từ giá ghế tại thời điểm đặt vé
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
