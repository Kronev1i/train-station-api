from rest_framework import viewsets, mixins
from apps.station.models import (
    Station,
    TrainType,
    Train,
    Route,
    Crew,
    Journey,
    Order
)
from apps.station.serializers import (
    StationSerializer,
    TrainTypeSerializer,
    TrainSerializer,
    RouteSerializer,
    CrewSerializer,
    JourneySerializer,
    OrderSerializer
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


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.select_related(
        "source",
        "destination"
    ).all()
    serializer_class = RouteSerializer


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class JourneyViewSet(viewsets.ModelViewSet):
    queryset = Journey.objects.select_related(
        "route",
        "train"
    ).prefetch_related(
        "crew"
    ).all()
    serializer_class = JourneySerializer


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Order.objects.prefetch_related(
        "tickets__journey__route",
        "tickets__journey__train"
    ).all()
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
