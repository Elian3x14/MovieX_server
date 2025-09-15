
from rest_framework import generics
from drf_spectacular.utils import extend_schema

from ..serializers import SeatTypeSerializer
from ..models import SeatType


@extend_schema(tags=["SeatTypes"])
class SeatTypeListCreateView(generics.ListCreateAPIView):
    queryset = SeatType.objects.all()
    serializer_class = SeatTypeSerializer


@extend_schema(tags=["SeatTypes"])
class SeatTypeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SeatType.objects.all()
    serializer_class = SeatTypeSerializer