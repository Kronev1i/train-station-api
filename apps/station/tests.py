from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.station.models import (
    Journey,
    Order,
    Route,
    Station,
    Ticket,
    Train,
    TrainType,
)

STATION_URL = reverse("station-list")
TRAIN_URL = reverse("train-list")
ROUTE_URL = reverse("route-list")
JOURNEY_URL = reverse("journey-list")
ORDER_URL = reverse("order-list")


def sample_station(**params):
    defaults = {
        "name": "Central Station",
        "latitude": 50.45,
        "longitude": 30.52,
    }
    defaults.update(params)
    return Station.objects.create(**defaults)


def sample_train(**params):
    if "train_type" not in params:
        params["train_type"] = TrainType.objects.create(
            name="Express-Type"
        )
    defaults = {
        "name": "Intercity 100",
        "cargo_num": 5,
        "places_in_cargo": 20,
    }
    defaults.update(params)
    return Train.objects.create(**defaults)


def sample_route(**params):
    if "source" not in params:
        params["source"] = sample_station(name="A")
    if "destination" not in params:
        params["destination"] = sample_station(name="B")
    defaults = {"distance": 500}
    defaults.update(params)
    return Route.objects.create(**defaults)


def sample_journey(**params):
    if "route" not in params:
        params["route"] = sample_route()
    if "train" not in params:
        params["train"] = sample_train()
    defaults = {
        "departure_time": timezone.now() + timezone.timedelta(days=1),
        "arrival_time": (
            timezone.now() + timezone.timedelta(days=1, hours=5)
        ),
    }
    defaults.update(params)
    return Journey.objects.create(**defaults)


class UnauthenticatedApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        urls = [
            STATION_URL,
            TRAIN_URL,
            ROUTE_URL,
            JOURNEY_URL,
            ORDER_URL,
        ]
        for url in urls:
            res = self.client.get(url)
            self.assertIn(
                res.status_code,
                [
                    status.HTTP_401_UNAUTHORIZED,
                    status.HTTP_403_FORBIDDEN,
                ],
            )


class PassengerApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="passenger",
            password="password123"
        )
        self.client.force_authenticate(self.user)

    def test_passenger_can_read_endpoints(self):
        sample_station()
        res = self.client.get(STATION_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_passenger_cannot_create_station(self):
        payload = {
            "name": "Forbidden Station",
            "latitude": 10.0,
            "longitude": 20.0,
        }
        res = self.client.post(STATION_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            username="adminuser",
            password="adminpassword"
        )
        self.client.force_authenticate(self.user)

    def test_admin_can_create_station(self):
        payload = {
            "name": "Admin Station",
            "latitude": 12.34,
            "longitude": 56.78,
        }
        res = self.client.post(STATION_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)


class OrderValidationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="buyer",
            password="password123"
        )
        self.client.force_authenticate(self.user)
        self.train = sample_train(cargo_num=2, places_in_cargo=10)
        self.journey = sample_journey(train=self.train)

    def test_create_order_valid_ticket(self):
        payload = {
            "tickets": [
                {"cargo": 1, "seat": 5, "journey": self.journey.id}
            ]
        }
        res = self.client.post(ORDER_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_order_invalid_cargo(self):
        payload = {
            "tickets": [
                {"cargo": 3, "seat": 5, "journey": self.journey.id}
            ]
        }
        res = self.client.post(ORDER_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_invalid_seat(self):
        payload = {
            "tickets": [
                {"cargo": 1, "seat": 11, "journey": self.journey.id}
            ]
        }
        res = self.client.post(ORDER_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)