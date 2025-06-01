from drf_spectacular.utils import extend_schema
from rest_framework import viewsets

from ..serializers import GenreSerializer
from ..models import Genre
from ..permissions import IsAdminOrReadOnly


@extend_schema(tags=["Genres"])
class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrReadOnly]