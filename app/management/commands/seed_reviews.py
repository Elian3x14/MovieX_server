from django.core.management.base import BaseCommand
from app.models import Review, Movie
from django.contrib.auth import get_user_model
from django.utils import timezone
import random

User = get_user_model()

class Command(BaseCommand):
    help = "Seed dữ liệu đánh giá phim (Review)"

    def handle(self, *args, **kwargs):
        users = User.objects.all()
        movies = Movie.objects.all()

        if not users.exists() or not movies.exists():
            self.stdout.write(self.style.ERROR("Cần có dữ liệu User và Movie trước khi seed Review."))
            return

        Review.objects.all().delete()  # Xoá tất cả đánh giá cũ (nếu cần)

        sample_comments = [
            "Phim rất hay, đáng xem!",
            "Tạm ổn, không quá ấn tượng.",
            "Nội dung hấp dẫn, kỹ xảo đỉnh cao.",
            "Không thích lắm, kết thúc hơi dở.",
            "Phim quá dài và hơi lan man.",
            "Diễn xuất tuyệt vời.",
            "Kịch bản hơi dễ đoán.",
            "Một tác phẩm đáng nhớ!",
            "Âm thanh và hình ảnh tuyệt hảo.",
            "Mình xem đến lần thứ hai rồi!",
        ]

        count = 0
        for user in users:
            for movie in random.sample(list(movies), k=min(5, len(movies))):  # mỗi user đánh giá 5 phim
                Review.objects.create(
                    author=user,
                    movie=movie,
                    rating=random.randint(5, 10),
                    comment=random.choice(sample_comments),
                    date=timezone.now() - timezone.timedelta(days=random.randint(0, 100)),
                )
                count += 1

        self.stdout.write(self.style.SUCCESS(f"Đã tạo {count} đánh giá phim (Review)."))
