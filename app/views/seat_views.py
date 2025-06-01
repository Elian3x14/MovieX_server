from rest_framework import generics
from drf_spectacular.utils import extend_schema

from ..serializers import SeatSerializer
from ..models import Seat



@extend_schema(tags=["Seats"])
class SeatCreateView(generics.CreateAPIView):
    queryset = Seat.objects.all()
    serializer_class = SeatSerializer
    # permission_classes = [permissions.IsAdminUser]


@extend_schema(tags=["Seats"])
class SeatDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Seat.objects.all()
    serializer_class = SeatSerializer
    # permission_classes = [permissions.IsAdminUser]