from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Chạy tất cả các seed commands cho hệ thống MovieX"

    def handle(self, *args, **kwargs):
        seed_commands = [
            "seed_users",
            "seed_genres",
            "seed_actors",
            "seed_seat_types",
            "seed_cinemas",
            "seed_rooms",
            "seed_movies",
            "seed_showtimes",
            "seed_reviews",
        ]

        for cmd in seed_commands:
            self.stdout.write(self.style.NOTICE(f"Đang chạy: {cmd}..."))
            call_command(cmd)
            self.stdout.write(self.style.SUCCESS(f"Đã chạy xong: {cmd}"))

        self.stdout.write(self.style.SUCCESS("Tất cả dữ liệu đã được seed thành công."))
