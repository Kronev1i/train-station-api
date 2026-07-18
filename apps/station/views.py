from rest_framework import viewsets
from apps.station.models import Station, TrainType, Train
from apps.station.serializers import (
    StationSerializer,
    TrainTypeSerializer,
    TrainSerializer
)


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer

class TrainTypeViewSet(viewsets.ModelViewSet):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer

class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.all()
    serializer_class = TrainSerializer
