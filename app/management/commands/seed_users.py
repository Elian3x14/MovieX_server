from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = "Seed tài khoản người dùng (admin & user mặc định)"

    def handle(self, *args, **kwargs):
        # Xóa toàn bộ người dùng trước (chỉ nên dùng khi đang phát triển)
        User.objects.all().delete()
        self.stdout.write(self.style.WARNING("Đã xóa toàn bộ người dùng."))

        admin_email = "admin@example.com"
        user_email = "user@example.com"

        if not User.objects.filter(email=admin_email).exists():
            User.objects.create_superuser(
                email=admin_email,
                username="admin",
                password="admin123",
                role="admin",
                phone_number="0900000001",
                first_name="Admin",
                last_name="User",
            )
            self.stdout.write(self.style.SUCCESS(f"Tạo admin: {admin_email}"))

        if not User.objects.filter(email=user_email).exists():
            User.objects.create_user(
                email=user_email,
                username="user",
                password="user123",
                role="user",
                phone_number="0900000002",
                first_name="Normal",
                last_name="User",
            )
            self.stdout.write(self.style.SUCCESS(f"Tạo user: {user_email}"))
