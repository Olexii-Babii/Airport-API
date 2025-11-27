from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import AirplaneType
from airport.serializers import AirplaneTypeSerializer

AIRPLANE_TYPE_URL = reverse("airport:airplanetype-list")

def sample_airplane_type(**params):
    default = {
        "name" : "test airplane type"
    }
    default.update(params)
    return AirplaneType.objects.create(**default)

class UnauthenticatedUserAirplaneTypeTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()


    def test_unauthenticated_airplane_type_list(self):
        response = self.client.get(AIRPLANE_TYPE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_unauthenticated_create_airplane_type(self):
        data = {"name": "test airplane type"}
        response = self.client.post(AIRPLANE_TYPE_URL, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedUserAirplaneTypeTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@gmail.com",
            password="test1234"
        )
        self.client.force_authenticate(self.user)

    def test_authenticated_airplane_type_list(self):
        sample_airplane_type(name="test2")
        sample_airplane_type(name="test3")
        response = self.client.get(AIRPLANE_TYPE_URL)
        serializer = AirplaneTypeSerializer(AirplaneType.objects.all(), many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_authenticated_create_airplane_type(self):
        data = {"name": "test airplane type"}
        response = self.client.post(AIRPLANE_TYPE_URL, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminUserAirplaneTypeTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            email="test@gmail.com",
            password="test1234"
        )
        self.client.force_authenticate(self.user)

    def test_admin_airplane_type_list(self):
        sample_airplane_type(name="test2")
        sample_airplane_type(name="test3")
        response = self.client.get(AIRPLANE_TYPE_URL)
        serializer = AirplaneTypeSerializer(AirplaneType.objects.all(), many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_admin_create_airplane_type(self):
        data = {"name": "test airplane type"}
        response = self.client.post(AIRPLANE_TYPE_URL, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
