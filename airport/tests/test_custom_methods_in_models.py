from django.contrib.auth import get_user_model
from django.test import TestCase

from airport.models import (
    Airport,
    Route,
    AirplaneType,
    Airplane,
    Flight,
    Crew,
    Order,
    Ticket,
)


class CustomMethodsInModelsTestCase(TestCase):
    def setUp(self):
        self.airport_1 = Airport.objects.create(
            name="Boruspil", closest_big_city="Kyiv"
        )
        self.airport_2 = Airport.objects.create(
            name="British airport", closest_big_city="London"
        )
        self.route = Route.objects.create(
            source=self.airport_1, destination=self.airport_2, distance=1000
        )
        self.airplane_type = AirplaneType.objects.create(name="Airbus 800")
        self.airplane = Airplane.objects.create(
            name="Airdream", rows=15, seats_in_row=10, airplane_type=self.airplane_type
        )
        self.flight = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time="2025-11-27T14:30:00Z",
            arrival_time="2025-11-28T14:30:00Z",
        )
        self.crew = Crew.objects.create(
            first_name="Tom",
            last_name="Wayne",
        )
        self.crew.flights.add(self.flight)
        self.user = get_user_model().objects.create_user(
            email="bobfisher@gmail.com", password="fisher1234"
        )
        self.order = Order.objects.create(
            user=self.user,
        )
        self.ticket = Ticket.objects.create(
            row=1, seat=1, flight=self.flight, order=self.order
        )

    def test_str_method_airport_model(self):
        self.assertEqual(self.airport_1.__str__(), self.airport_1.name)

    def test_str_method_route_model(self):
        self.assertEqual(
            self.route.__str__(),
            (
                f"{self.route.source.name}({self.route.source.closest_big_city}) "
                f"-> {self.route.destination.name}({self.route.destination.closest_big_city}) "
            ),
        )

    def test_str_method_airplane_type_model(self):
        self.assertEqual(self.airplane_type.__str__(), self.airplane_type.name)

    def test_str_method_airplane_model(self):
        self.assertEqual(
            self.airplane.__str__(),
            f"Name: {self.airplane.name}, type: {self.airplane.airplane_type.name}",
        )

    def test_str_method_flight_model(self):
        self.assertEqual(
            self.flight.__str__(),
            (
                f"{self.flight.route.source.closest_big_city} -> {self.flight.route.destination.closest_big_city} "
                f"departure time: {self.flight.departure_time} "
                f"arrival time: {self.flight.arrival_time}"
            ),
        )

    def test_str_method_crew_model(self):
        self.assertEqual(
            self.crew.__str__(), f"{self.crew.first_name} {self.crew.last_name}"
        )

    def test_str_method_order_model(self):
        self.assertEqual(self.order.__str__(), f"Created at: {self.order.created_at}")

    def test_str_method_ticket_model(self):
        self.assertEqual(
            self.ticket.__str__(),
            f"{self.ticket.flight.route}, {self.ticket.row} -> {self.ticket.seat}",
        )

    def test_course_method_route_model(self):
        self.assertEqual(
            self.route.course,
            f"{self.route.source.closest_big_city} -> {self.route.destination.closest_big_city}",
        )

    def test_capacity_method_airplane_model(self):
        self.assertEqual(
            self.airplane.capacity, self.airplane.rows * self.airplane.seats_in_row
        )
