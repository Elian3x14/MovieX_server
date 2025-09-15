from rest_framework import generics
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404 

from ..serializers import SeatSerializer, SeatRoomSerializer
from ..models import Seat, Room



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
    
@extend_schema(tags=["Seats"])  
class SeatByRoomView(generics.ListAPIView):
    serializer_class = SeatRoomSerializer

    def get_queryset(self):
        room_id = self.kwargs.get("room_id")
        # Kiểm tra phòng có tồn tại hay không
        get_object_or_404(Room, id=room_id)
       
        return Seat.objects.filter(room_id=room_id)