from rest_framework import generics, permissions, viewsets
from drf_spectacular.utils import extend_schema

from django.utils import timezone

from ..serializers import MovieSerializer, ShowtimeSerializer, ReviewSerializer
from ..pagination import MovieReviewPagination
from ..models import Movie, Showtime, Review
from ..permissions import IsAdminOrReadOnly

@extend_schema(tags=["Movies"])
class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "id"  # Nếu bạn muốn dùng `id` thay vì mặc định `pk`

@extend_schema(tags=["Movies"])
class ShowtimeListView(generics.ListAPIView):
    serializer_class = ShowtimeSerializer

    def get_queryset(self):
        movie_id = self.kwargs["movie_id"]
        now = timezone.now()
        return Showtime.objects.filter(movie_id=movie_id, end_time__gt=now)
    

@extend_schema(
    tags=["Movies"],
)
class MovieReviewList(generics.ListAPIView):
    serializer_class = ReviewSerializer
    pagination_class = MovieReviewPagination
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        movie_id = self.kwargs["movie_id"]
        return Review.objects.filter(movie_id=movie_id).order_by("-date")
