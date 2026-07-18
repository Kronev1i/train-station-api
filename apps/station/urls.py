from rest_framework import routers
from apps.station.views import (
    StationViewSet,
    TrainTypeViewSet,
    TrainViewSet,
    RouteViewSet,
    CrewViewSet,
    JourneyViewSet,
    OrderViewSet
)


router = routers.DefaultRouter()
router.register("stations", StationViewSet)
router.register("train_types", TrainTypeViewSet)
router.register("trains", TrainViewSet)
router.register("routes", RouteViewSet)
router.register("crews", CrewViewSet)
router.register("journeys", JourneyViewSet)
router.register("orders", OrderViewSet)

urlpatterns = router.urls
