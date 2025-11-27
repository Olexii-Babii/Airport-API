from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Airport, Route
from airport.serializers import RouteListSerializer, RouteDetailSerializer

ROUTE_URL = reverse("airport:route-list")

def sample_airport(**params):
    default = {
        "name" : "test airport",
        "closest_big_city" : "test big city",
    }
    default.update(params)
    return Airport.objects.create(**default)

def sample_route(**params):
    source = sample_airport(
        name="source",
        closest_big_city="big city 1"
    )
    destination = sample_airport(
        name="destination",
        closest_big_city="big city 2"
    )
    default = {
        "distance" : 1000,
        "source" : source,
        "destination" : destination,
    }
    default.update(params)
    return Route.objects.create(**default)

class UnauthenticatedUserRouteTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.source = sample_airport(name="source")
        self.destination = sample_airport(name="destination")
        sample_route()

    def test_unauthenticated_route_list(self):
        response = self.client.get(ROUTE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_unauthenticated_create_route(self):
        data = {
            "source" : self.source.id,
            "destination" : self.destination.id,
            "distance" : 1000
        }
        response = self.client.post(ROUTE_URL, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_retrieve_route(self):
        response = self.client.get(reverse("airport:route-detail", kwargs={"pk" : 1}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedUserRouteTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@gmail.com",
            password="test1234"
        )
        sample_route()
        self.source = sample_airport(name="source")
        self.destination = sample_airport(name="destination")
        self.client.force_authenticate(self.user)

    def test_authenticated_route_list(self):
        sample_route(
            distance=500,
            source=sample_airport(
                name="test airport 1",
                closest_big_city="big city 1"
        ),
            destination=sample_airport(
                name="test airport 2",
                closest_big_city="big city 2"
        ),
            )

        sample_route(
            distance=250,
            source=sample_airport(
                name="test airport 3",
                closest_big_city="big city 3"
            ),
            destination=sample_airport(
                name="test airport 4",
                closest_big_city="big city 4"
            ),
        )
        response = self.client.get(ROUTE_URL)
        serializer = RouteListSerializer(Route.objects.all(), many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_authenticated_create_route(self):
        data = {
            "source": self.source.id,
            "destination": self.destination.id,
            "distance": 1000
        }
        response = self.client.post(ROUTE_URL, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_retrieve_route(self):
        response = self.client.get(reverse("airport:route-detail", kwargs={"pk" : 1}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AdminUserRouteTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            email="test@gmail.com",
            password="test1234"
        )
        sample_route()
        self.source = sample_airport(name="source")
        self.destination = sample_airport(name="destination")
        self.client.force_authenticate(self.user)

    def test_admin_route_list(self):
        sample_route(
            distance=400,
            source=sample_airport(
                name="test airport 1",
                closest_big_city="big city 1"
            ),
            destination=sample_airport(
                name="test airport 2",
                closest_big_city="big city 2"
            ),
        )

        sample_route(
            distance=300,
            source=sample_airport(
                name="test airport 3",
                closest_big_city="big city 3"
            ),
            destination=sample_airport(
                name="test airport 4",
                closest_big_city="big city 4"
            ),
        )
        response = self.client.get(ROUTE_URL)
        serializer = RouteListSerializer(Route.objects.all(), many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_admin_create_route(self):
        data = {
            "source": self.source.id,
            "destination": self.destination.id,
            "distance": 1000
        }
        response = self.client.post(ROUTE_URL, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admin_retrieve_route(self):
        sample_route(
            distance=300,
            source=sample_airport(
                name="test airport 3",
                closest_big_city="big city 3"
            ),
            destination=sample_airport(
                name="test airport 4",
                closest_big_city="big city 4"
            ),
        )
        response = self.client.get(reverse("airport:route-detail", kwargs={"pk" : 1}))
        serializer = RouteDetailSerializer(Route.objects.get(pk=1), many=False)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
