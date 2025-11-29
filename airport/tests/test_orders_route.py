from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import (
    AirplaneType,
    Airplane,
    Route,
    Airport,
    Flight,
    Crew,
    Order,
    Ticket,
)
from airport.serializers import OrderListSerializer

ORDER_URL = reverse("airport:order-list")


def sample_airplane_type(**params):
    default = {"name": "test airplane type"}
    default.update(params)
    return AirplaneType.objects.create(**default)


def sample_airplane(airplane_type: str = None, **params):
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


def sample_flight(airplane_type: str = None, **params):
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


def sample_crew(airplane_type: str = None, **params):
    default = {
        "first_name": "Test first name",
        "last_name": "Test last name",
    }

    if airplane_type:
        flights = sample_flight(airplane_type)
    elif "flights" in params:
        flights = params.pop("flights")
    else:
        flights = sample_flight()

    default.update(params)
    crew = Crew.objects.create(**default)
    crew.flights.add(flights)
    crew.save()
    return crew


class UnauthenticatedUserOrderTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@gmail.com", password="test1234"
        )
        self.flight = sample_flight(airplane_type="Order type")
        self.order = Order.objects.create(user=self.user)

    def test_unauthenticated_order_list(self):
        response = self.client.get(ORDER_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_create_order(self):
        data = {
            "tickets": [
                {"row": 1, "seat": 1, "flight": self.flight.id},
            ]
        }
        response = self.client.post(ORDER_URL, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_retrieve_order(self):
        response = self.client.get(reverse("airport:order-detail", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedUserOrderTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@gmail.com", password="test1234"
        )
        self.mock_user = get_user_model().objects.create_user(
            email="mockuser@gmail.com", password="mock1234"
        )
        self.order = Order.objects.create(user=self.user)
        Order.objects.create(user=self.mock_user)
        self.flight = sample_flight(airplane_type="Order type")
        self.client.force_authenticate(self.user)

    def test_authenticated_order_list_with_only_your_orders(self):
        response = self.client.get(ORDER_URL)
        serializer = OrderListSerializer(
            Order.objects.filter(user=self.user), many=True
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_authenticated_create_order(self):
        data = {
            "tickets": [
                {"row": 1, "seat": 1, "flight": self.flight.id},
            ]
        }
        response = self.client.post(ORDER_URL, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_order_with_bought_ticket(self):
        Ticket.objects.create(row=1, seat=1, flight=self.flight, order=self.order)
        data = {
            "tickets": [
                {"row": 1, "seat": 1, "flight": self.flight.id},
            ]
        }
        response = self.client.post(ORDER_URL, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_with_ticket_with_no_valid_data(self):
        data = {
            "tickets": [
                {"row": 999, "seat": 999, "flight": self.flight.id},
            ]
        }
        response = self.client.post(ORDER_URL, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_authenticated_retrieve_order(self):
        response = self.client.get(reverse("airport:order-detail", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AdminUserOrderTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            email="test@gmail.com", password="test1234"
        )
        self.mock_user = get_user_model().objects.create_user(
            email="mockuser@gmail.com", password="mock1234"
        )
        Order.objects.create(user=self.user)
        Order.objects.create(user=self.mock_user)
        self.flight = sample_flight(airplane_type="Order type")
        self.client.force_authenticate(self.user)

    def test_admin_order_list(self):
        response = self.client.get(ORDER_URL)
        serializer = OrderListSerializer(
            Order.objects.filter(user=self.user), many=True
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_admin_create_order(self):
        data = {
            "tickets": [
                {"row": 1, "seat": 1, "flight": self.flight.id},
            ]
        }
        response = self.client.post(ORDER_URL, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admin_retrieve_order(self):
        response = self.client.get(reverse("airport:order-detail", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
