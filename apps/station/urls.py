from rest_framework import routers
from apps.station.views import (
    StationViewSet,
    TrainTypeViewSet,
    TrainViewSet
)


router = routers.DefaultRouter()
router.register("stations", StationViewSet)
router.register("train_types", TrainTypeViewSet)
router.register("trains", TrainViewSet)

urlpatterns = router.urls