from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import AirplaneType, Airplane, Route, Airport, Flight, Crew
from airport.serializers import CrewListSerializer

CREW_URL = reverse("airport:crew-list")


def sample_airplane_type(**params):
    default = {
        "name" : "test airplane type"
    }
    default.update(params)
    return AirplaneType.objects.create(**default)

def sample_airplane(airplane_type: str = None, **params):
    if not airplane_type:
        airplane_type = sample_airplane_type()

    default = {
        "name" : "test airplane",
        "rows" : 15,
        "seats_in_row" : 20,
        "airplane_type" : airplane_type
    }
    default.update(params)
    return Airplane.objects.create(**default)

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

def sample_flight(airplane_type: str = None, **params):
    if airplane_type:
        airplane = sample_airplane(
            airplane_type=sample_airplane_type(
                name=airplane_type
            )
        )
    else:
        airplane = sample_airplane()

    default = {
        "route" : sample_route(),
        "airplane" : airplane,
        "departure_time" : "2025-11-27T14:30:00Z",
        "arrival_time" : "2024-11-28T19:00:00Z"
    }
    default.update(params)
    return Flight.objects.create(**default)

def sample_crew(airplane_type: str = None, **params):
    default = {
        "first_name" : "Test first name",
        "last_name" : "Test last name",
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

class UnauthenticatedUserCrewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        sample_crew()
        self.flights = sample_flight(
            airplane_type="New test crew type"
        )

    def test_unauthenticated_crew_list(self):
        response = self.client.get(CREW_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_unauthenticated_create_crew(self):
        data = {
            "first_name" : "Test crew first name",
            "last_name" : "Test crew last name",
            "flights" : self.flights.id
        }
        response = self.client.post(CREW_URL, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedUserCrewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@gmail.com",
            password="test1234"
        )

        sample_crew()
        self.flights = sample_flight(
            airplane_type="New test crew type"
        )

        self.client.force_authenticate(self.user)

    def test_authenticated_crew_list(self):
        sample_crew(
            airplane_type="crew airplane type 2"
        )

        sample_crew(
            airplane_type="crew airplane type 3"
        )
        response = self.client.get(CREW_URL)
        serializer = CrewListSerializer(Crew.objects.all(), many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_authenticated_create_crew(self):
        data = {
            "first_name": "Test crew first name",
            "last_name": "Test crew last name",
            "flights": self.flights.id
        }
        response = self.client.post(CREW_URL, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminUserAirplaneTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            email="test@gmail.com",
            password="test1234"
        )
        sample_crew()
        self.flights =sample_flight(
                airplane_type="New test crew type"
        )
        self.client.force_authenticate(self.user)

    def test_admin_crew_list(self):
        sample_crew(
            airplane_type="crew airplane type 2"
        )

        sample_crew(
            airplane_type="crew airplane type 3"
        )
        response = self.client.get(CREW_URL)
        serializer = CrewListSerializer(Crew.objects.all(), many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_admin_create_flight(self):
        data = {
            "first_name": "Test crew first name",
            "last_name": "Test crew last name",
            "flights": self.flights.id
        }
        response = self.client.post(CREW_URL, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
