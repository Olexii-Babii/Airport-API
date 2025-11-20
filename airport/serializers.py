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