from drf_spectacular.utils import extend_schema
from rest_framework import viewsets

from ..serializers import RoomSerializer
from ..models import Room
from ..permissions import IsAdminOrReadOnly

@extend_schema(tags=["Rooms"])  # Gắn tag cho tài liệu API
class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "id"  # Nếu bạn dùng id thay vì pk
