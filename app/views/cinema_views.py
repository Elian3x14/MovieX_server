from rest_framework import viewsets
from drf_spectacular.utils import extend_schema

from ..serializers import CinemaSerializer
from ..models import Cinema
from ..permissions import IsAdminOrReadOnly

@extend_schema(tags=["Cinemas"])
class CinemaViewSet(viewsets.ModelViewSet):
    queryset = Cinema.objects.all()
    serializer_class = CinemaSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "id"  # Nếu bạn dùng id thay vì pk
