from drf_spectacular.utils import extend_schema
from rest_framework import viewsets

from ..serializers import ActorSerializer
from ..models import Actor
from ..permissions import IsAdminOrReadOnly


@extend_schema(tags=["Actors"])
class ActorViewSet(viewsets.ModelViewSet):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer
    permission_classes = [IsAdminOrReadOnly]