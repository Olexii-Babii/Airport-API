from django.contrib.auth import get_user_model
from django.db.models import F, Count, Q
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import AirplaneType, Airplane, Route, Airport, Flight
from airport.serializers import FlightListSerializer

FLIGHT_URL = reverse("airport:flight-list")


def flight_queryset():
    return Flight.objects.annotate(
        available_seats=(F("airplane__rows") * F("airplane__seats_in_row"))
        - Count("tickets")
    ).order_by("id")


def sample_airplane_type(**params):
    default = {"name": "test airplane type"}
    default.update(params)
    return AirplaneType.objects.create(**default)


def sample_airplane(airplane_type=None, **params):
    if not airplane_type:
        airplane_type = sample_airplane_type()

    default = {
        "name": "test airplane",
        "rows": 15,
        "seats_in_row": 20,
        "airplane_type": airplane_type,
    }
    default.update(params)
    return Airplane.objects.create(**default)


def sample_airport(**params):
    default = {
        "name": "test airport",
        "closest_big_city": "test big city",
    }
    default.update(params)
    return Airport.objects.create(**default)


def sample_route(**params):
    source = sample_airport(name="source", closest_big_city="big city 1")
    destination = sample_airport(name="destination", closest_big_city="big city 2")
    default = {
        "distance": 1000,
        "source": source,
        "destination": destination,
    }
    default.update(params)
    return Route.objects.create(**default)


def sample_flight(airplane_type=None, **params):
    if airplane_type:
        airplane = sample_airplane(
            airplane_type=sample_airplane_type(name=airplane_type)
        )
    else:
        airplane = sample_airplane()

    default = {
        "route": sample_route(),
        "airplane": airplane,
        "departure_time": "2025-11-27T14:30:00Z",
        "arrival_time": "2024-11-28T19:00:00Z",
    }
    default.update(params)
    return Flight.objects.create(**default)


class UnauthenticatedUserFlightTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        sample_flight()

    def test_unauthenticated_flight_list(self):
        response = self.client.get(FLIGHT_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_create_flight(self):
        data = {
            "route": sample_route(),
            "airplane": sample_airplane(
                airplane_type=sample_airplane_type(name="flight test type")
            ),
            "departure_time": "2025-11-28T14:30:00Z",
            "arrival_time": "2024-11-29T19:00:00Z",
        }
        response = self.client.post(FLIGHT_URL, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_retrieve_flight(self):
        response = self.client.get(reverse("airport:flight-detail", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_update_flight(self):
        data = {
            "departure_time": "2025-11-29T14:30:00Z",
            "arrival_time": "2024-11-30T19:00:00Z",
        }
        response = self.client.patch(
            reverse("airport:flight-detail", kwargs={"pk": 1}), data
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_delete_flight(self):
        response = self.client.delete(
            reverse("airport:flight-detail", kwargs={"pk": 1})
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedUserFlightTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@gmail.com", password="test1234"
        )
        self.airplane = sample_airplane(
            airplane_type=sample_airplane_type(name="flight test type")
        )
        self.route = sample_route()
        sample_flight()

        self.client.force_authenticate(self.user)

    def test_authenticated_flight_list(self):
        sample_flight(airplane_type="fight airplane type 2")

        sample_flight(airplane_type="flight airplane type 3")
        response = self.client.get(FLIGHT_URL)
        serializer = FlightListSerializer(
            Flight.objects.annotate(
                available_seats=(F("airplane__rows") * F("airplane__seats_in_row"))
                - Count("tickets")
            ).order_by("id"),
            many=True,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_authenticated_create_flight(self):
        data = {
            "route": self.route.id,
            "airplane": self.route.id,
            "departure_time": "2025-11-28T14:30:00Z",
            "arrival_time": "2024-11-29T19:00:00Z",
        }
        response = self.client.post(FLIGHT_URL, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_retrieve_flight(self):
        response = self.client.get(reverse("airport:flight-detail", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authenticated_update_flight(self):
        data = {
            "departure_time": "2025-11-29T14:30:00Z",
            "arrival_time": "2024-11-30T19:00:00Z",
        }
        response = self.client.patch(
            reverse("airport:flight-detail", kwargs={"pk": 1}), data
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_delete_flight(self):
        response = self.client.delete(
            reverse("airport:flight-detail", kwargs={"pk": 1})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminUserAirplaneTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            email="test@gmail.com", password="test1234"
        )
        self.airplane = sample_airplane(
            airplane_type=sample_airplane_type(name="flight test type")
        )
        self.route = sample_route()
        sample_flight()

        self.client.force_authenticate(self.user)

    def test_admin_flight_list(self):
        sample_flight(airplane_type="fight airplane type 2")

        sample_flight(airplane_type="flight airplane type 3")
        response = self.client.get(FLIGHT_URL)
        serializer = FlightListSerializer(flight_queryset(), many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_admin_create_flight(self):
        data = {
            "route": self.route.id,
            "airplane": self.airplane.id,
            "departure_time": "2025-11-28T14:30:00Z",
            "arrival_time": "2024-11-29T19:00:00Z",
        }
        response = self.client.post(FLIGHT_URL, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admin_retrieve_flight(self):
        response = self.client.get(reverse("airport:flight-detail", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_update_flight(self):
        data = {
            "departure_time": "2025-11-29T14:30:00Z",
            "arrival_time": "2024-11-30T19:00:00Z",
        }
        response = self.client.patch(
            reverse("airport:flight-detail", kwargs={"pk": 1}), data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_delete_flight(self):
        response = self.client.delete(
            reverse("airport:flight-detail", kwargs={"pk": 1})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class FilterFlightQuerysetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            email="test@gmail.com", password="test1234"
        )
        self.airport_1 = sample_airport(
            name="Test Airport Barcelona", closest_big_city="Barcelona"
        )
        self.airport_2 = sample_airport(
            name="Test Airport London", closest_big_city="London"
        )
        self.airport_3 = sample_airport(
            name="Test Airport Berlin", closest_big_city="Berlin"
        )
        self.route_1 = sample_route(
            source=self.airport_1, destination=self.airport_2, distance=500
        )
        self.route_2 = sample_route(
            source=self.airport_2, destination=self.airport_3, distance=1000
        )
        self.route_3 = sample_route(
            source=self.airport_3, destination=self.airport_1, distance=600
        )

        sample_flight(
            route=self.route_1,
            airplane_type="Boing 737",
            departure_time="2025-10-28T14:30:00Z",
            arrival_time="2024-10-30T19:00:00Z",
        )
        sample_flight(
            route=self.route_2,
            airplane_type="Airbus 800",
            departure_time="2025-11-28T14:30:00Z",
            arrival_time="2024-11-30T19:00:00Z",
        )
        sample_flight(
            route=self.route_3,
            airplane_type="AN-12",
            departure_time="2025-12-28T14:30:00Z",
            arrival_time="2024-12-30T19:00:00Z",
        )

        self.client.force_authenticate(self.user)

    def test_correct_filter_by_source(self):
        response = self.client.get(FLIGHT_URL + "?source=bar")
        serializer = FlightListSerializer(
            flight_queryset().filter(
                Q(route__source__name__icontains="bar")
                | Q(route__source__closest_big_city__icontains="bar")
            ),
            many=True,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_correct_filter_by_destination(self):
        response = self.client.get(FLIGHT_URL + "?destination=ber")
        serializer = FlightListSerializer(
            flight_queryset().filter(
                Q(route__destination__name__icontains="ber")
                | Q(route__destination__closest_big_city__icontains="ber")
            ),
            many=True,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_correct_filter_by_departure_time(self):
        response = self.client.get(FLIGHT_URL + "?departure_time=2024-12-30")
        serializer = FlightListSerializer(
            flight_queryset().filter(departure_time__date="2024-12-30"), many=True
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_correct_filter_by_arrival_time(self):
        response = self.client.get(FLIGHT_URL + "?arrival_time=2024-11-30")
        serializer = FlightListSerializer(
            flight_queryset().filter(arrival_time__date="2024-11-30"), many=True
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_return_all_flights(self):
        response = self.client.get(FLIGHT_URL)
        serializer = FlightListSerializer(flight_queryset(), many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_return_zero_flights(self):
        response = self.client.get(FLIGHT_URL + "?source=test1234")
        serializer = FlightListSerializer(
            Flight.objects.filter(
                Q(route__source__name__icontains="test1234")
                | Q(route__source__closest_big_city__icontains="test1234")
            ),
            many=True,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)
