from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator

# Regex cho số điện thoại Việt Nam: 10 số, bắt đầu bằng 03, 05, 07, 08, 09
vietnam_phone_regex = RegexValidator(
    regex=r"^(03|05|07|08|09)\d{8}$",
    message="Số điện thoại không hợp lệ. Vui lòng nhập số 10 chữ số bắt đầu bằng 03, 05, 07, 08, hoặc 09.",
)