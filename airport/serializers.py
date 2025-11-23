from django.db import transaction
from rest_framework import serializers

from airport.models import (
    Airport,
    Airplane,
    AirplaneType,
    Crew,
    Route,
    Flight,
    Order,
    Ticket
)


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = "__all__"


class AirportRouteSerializer(serializers.ModelSerializer):
    airport = serializers.CharField(read_only=True, source="name")
    city = serializers.CharField(read_only=True, source="closest_big_city")
    class Meta:
        model = Airport
        fields = ("airport", "city")

class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = "__all__"


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = "__all__"


class AirplaneListSerializer(serializers.ModelSerializer):
    airplane_type = serializers.CharField(read_only=True, source="airplane_type.name")
    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row", "capacity" , "airplane_type")


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = "__all__"


class RouteListSerializer(serializers.ModelSerializer):
    source = serializers.CharField(read_only=True, source="source.closest_big_city")
    destination = serializers.CharField(read_only=True, source="destination.closest_big_city")

    class Meta:
        model = Route
        fields = "__all__"


class RouteDetailSerializer(serializers.ModelSerializer):
    source = AirportRouteSerializer(read_only=True)
    destination = AirportRouteSerializer(read_only=True)

    class Meta:
        model = Route
        fields = "__all__"


class FlightSerializer(serializers.ModelSerializer):
    route = serializers.PrimaryKeyRelatedField(
        queryset=Route.objects.select_related("source", "destination")
    )
    airplane = serializers.PrimaryKeyRelatedField(
        queryset=Airplane.objects.select_related("airplane_type")
    )
    class Meta:
        model = Flight
        fields = "__all__"


class FlightListSerializer(serializers.ModelSerializer):
    route = serializers.StringRelatedField(read_only=True, many=False)
    airplane = serializers.StringRelatedField(read_only=True, many=False)
    available_seats = serializers.IntegerField(read_only=True)
    class Meta:
        model = Flight
        fields = "__all__"


class FlightDetailSerializer(serializers.ModelSerializer):
    route = RouteDetailSerializer(read_only=True)
    airplane = AirplaneListSerializer(read_only=True)
    taken_seats = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="seat",
        source="tickets"
    )

    class Meta:
        model = Flight
        fields = "__all__"


class CrewSerializer(serializers.ModelSerializer):
    flights = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Flight.objects.select_related(
            "route__source",
            "route__destination"
        ))
    class Meta:
        model = Crew
        fields = "__all__"


class CrewListSerializer(serializers.ModelSerializer):
    flights = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="route.course",
    )

    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "flights")


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight")


class TicketOrderSerializer(serializers.ModelSerializer):
    flight = serializers.CharField(read_only=True, source="flight.route")

    class Meta:
        model = Ticket
        fields = ("id", "seat", "flight")


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(read_only=False, many=True, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "tickets", "created_at")

    def create(self, validated_data):
        with transaction.atomic():
            ticket_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket in ticket_data:
                Ticket.objects.create(order=order, **ticket)
            return order


class OrderListSerializer(serializers.ModelSerializer):
    tickets = TicketOrderSerializer(read_only=True, many=True)

    class Meta:
        model = Order
        fields = ("id", "tickets", "created_at")