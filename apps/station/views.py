from datetime import datetime

from django.db.models import Count, F
from rest_framework import mixins, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from apps.station.models import (
    Crew,
    Journey,
    Order,
    Route,
    Station,
    Train,
    TrainType,
)
from apps.station.permissions import IsAdminOrIfAuthenticatedReadOnly
from apps.station.serializers import (
    CrewSerializer,
    JourneyDetailSerializer,
    JourneyListSerializer,
    JourneySerializer,
    OrderListSerializer,
    OrderSerializer,
    RouteListSerializer,
    RouteSerializer,
    StationSerializer,
    TrainListSerializer,
    TrainSerializer,
    TrainTypeSerializer,
)


class OrderPagination(PageNumberPagination):
    page_size = 5
    max_page_size = 50


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        name = self.request.query_params.get("name")
        queryset = self.queryset
        if name:
            queryset = queryset.filter(name__icontains=name)
        return queryset


class TrainTypeViewSet(viewsets.ModelViewSet):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.select_related("train_type")
    serializer_class = TrainSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return TrainListSerializer
        return TrainSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.select_related("source", "destination")
    serializer_class = RouteSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return RouteListSerializer
        return RouteSerializer


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class JourneyViewSet(viewsets.ModelViewSet):
    queryset = (
        Journey.objects.all()
        .select_related(
            "route__source",
            "route__destination",
            "train__train_type"
        )
        .prefetch_related("crew")
        .annotate(
            tickets_available=(
                F("train__cargo_num") * F("train__places_in_cargo")
                - Count("tickets")
            )
        )
    )
    serializer_class = JourneySerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        date = self.request.query_params.get("date")
        route_id = self.request.query_params.get("route")
        queryset = self.queryset

        if date:
            try:
                date_object = datetime.strptime(date, "%Y-%m-%d").date()
                queryset = queryset.filter(departure_time__date=date_object)
            except ValueError:
                pass

        if route_id:
            queryset = queryset.filter(route_id=int(route_id))

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return JourneyListSerializer
        if self.action == "retrieve":
            return JourneyDetailSerializer
        return JourneySerializer


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Order.objects.prefetch_related(
        "tickets__journey__route__source",
        "tickets__journey__route__destination",
        "tickets__journey__train",
    )
    serializer_class = OrderSerializer
    pagination_class = OrderPagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)