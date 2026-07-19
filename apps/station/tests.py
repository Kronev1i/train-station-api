from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.station.models import Station, TrainType, Train
from apps.station.serializers import StationSerializer, TrainSerializer

STATION_URL = reverse("station-list")
TRAIN_URL = reverse("train-list")


def sample_station(**params):
    defaults = {
        "name": "Test Station",
        "latitude": 50.0,
        "longitude": 20.0,
    }
    defaults.update(params)
    return Station.objects.create(**defaults)


def sample_train(**params):
    train_type = TrainType.objects.create(name="Default Type")
    defaults = {
        "name": "Test Train",
        "cargo_num": 5,
        "places_in_cargo": 20,
        "train_type": train_type,
    }
    defaults.update(params)
    return Train.objects.create(**defaults)


class UnauthenticatedStationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_list_stations(self):
        sample_station()
        res = self.client.get(STATION_URL)
        stations = Station.objects.all()
        serializer = StationSerializer(stations, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


class AuthenticatedTrainApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com", "testpass"
        )
        self.client.force_authenticate(self.user)

    def test_list_trains(self):
        sample_train()
        res = self.client.get(TRAIN_URL)
        trains = Train.objects.all()
        serializer = TrainSerializer(trains, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_train(self):
        train_type = TrainType.objects.create(name="Express")
        payload = {
            "name": "New Express",
            "cargo_num": 10,
            "places_in_cargo": 30,
            "train_type": train_type.id,
        }
        res = self.client.post(TRAIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        train = Train.objects.get(id=res.data["id"])
        for key in payload.keys():
            if key == "train_type":
                self.assertEqual(getattr(train, key).id, payload[key])
            else:
                self.assertEqual(getattr(train, key), payload[key])


class AdminOrderApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "admin@admin.com", "password"
        )
        self.client.force_authenticate(self.user)

    def test_create_order_forbidden(self):
        # Пример того, как тестировать методы, если они ограничены
        res = self.client.get(reverse("order-list"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
