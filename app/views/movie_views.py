from rest_framework import generics, permissions
from drf_spectacular.utils import extend_schema

from django.utils import timezone

from ..serializers import MovieSerializer, ShowtimeSerializer, ReviewSerializer
from ..pagination import MovieReviewPagination
from ..models import Movie, Showtime, Review


@extend_schema(tags=["Movies"])
class MovieListView(generics.ListAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [permissions.AllowAny]  # Không cần đăng nhập


@extend_schema(tags=["Movies"])
class MovieDetailView(generics.RetrieveAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [permissions.AllowAny]  # Không cần đăng nhập
    lookup_field = "id"  # Mặc định là 'pk', bạn dùng 'id' nếu muốn rõ ràng hơn


@extend_schema(tags=["Movies"])
class MovieCreateView(generics.CreateAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [permissions.IsAdminUser]


@extend_schema(tags=["Movies"])
class MovieUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [permissions.IsAdminUser]

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
