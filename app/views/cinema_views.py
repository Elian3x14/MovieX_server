from rest_framework import generics
from drf_spectacular.utils import extend_schema

from ..serializers import CinemaSerializer
from ..models import Cinema

@extend_schema(tags=["Cinemas"])
class CinemaListCreateView(generics.ListCreateAPIView):
    queryset = Cinema.objects.all()
    serializer_class = CinemaSerializer


@extend_schema(tags=["Cinemas"])
class CinemaRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Cinema.objects.all()
    serializer_class = CinemaSerializer
