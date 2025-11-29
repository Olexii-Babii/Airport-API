from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Airport
from airport.serializers import AirportSerializer

AIRPORT_URL = reverse("airport:airport-list")


def sample_airport(**params):
    default = {
        "name": "test airport",
        "closest_big_city": "test big city",
    }
    default.update(params)
    return Airport.objects.create(**default)


class UnauthenticatedUserAirportTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_unauthenticated_airport_list(self):
        response = self.client.get(AIRPORT_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_create_airport(self):
        data = {
            "name": "test airport",
            "closest_big_city": "test big city",
        }
        response = self.client.post(AIRPORT_URL, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedUserAirportTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@gmail.com", password="test1234"
        )
        self.client.force_authenticate(self.user)

    def test_authenticated_airport_list(self):
        sample_airport(name="test2", closest_big_city="test big city 1")
        sample_airport(name="test3", closest_big_city="test big city 2")
        response = self.client.get(AIRPORT_URL)
        serializer = AirportSerializer(Airport.objects.all(), many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_authenticated_create_airport(self):
        data = {"name": "test airport", "closest_big_city": "test big city 3"}
        response = self.client.post(AIRPORT_URL, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminUserAirplaneTypeTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            email="test@gmail.com", password="test1234"
        )
        self.client.force_authenticate(self.user)

    def test_admin_airport_list(self):
        sample_airport(name="test2", closest_big_city="test big city 1")
        sample_airport(name="test3", closest_big_city="test big city 2")
        response = self.client.get(AIRPORT_URL)
        serializer = AirportSerializer(Airport.objects.all(), many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_admin_create_airport(self):
        data = {"name": "test airport", "closest_big_city": "test big city 3"}
        response = self.client.post(AIRPORT_URL, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
