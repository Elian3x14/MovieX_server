from django.core.management.base import BaseCommand
from app.models import Genre

class Command(BaseCommand):
    help = "Seed genres"

    def handle(self, *args, **kwargs):
        genre_names = [
            "Hành động", "Phiêu lưu", "Hài", "Tâm lý", "Giả tưởng",
            "Kinh dị", "Lãng mạn", "Khoa học viễn tưởng", "Hồi hộp", "Hoạt hình"
        ]
        created = 0
        for name in genre_names:
            _, is_created = Genre.objects.get_or_create(name=name)
            if is_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f"Đã seed {created} thể loại phim."))
