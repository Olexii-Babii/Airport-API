from django.db.models import Count, F, Q, Prefetch
from rest_framework import viewsets

from airport.models import (
    Airport,
    AirplaneType,
    Airplane,
    Crew,
    Route,
    Flight,
    Order, Ticket,
)
from airport.permissions import IsAdminUserOrIsAuthenticatedReadOnly

from airport.serializers import (
    AirportSerializer,
    AirplaneTypeSerializer,
    AirplaneSerializer,
    AirplaneListSerializer,
    RouteSerializer,
    RouteListSerializer,
    RouteDetailSerializer,
    FlightSerializer,
    FlightListSerializer,
    FlightDetailSerializer,
    CrewSerializer,
    CrewListSerializer,
    OrderSerializer,
    OrderListSerializer,
)


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = (IsAdminUserOrIsAuthenticatedReadOnly,)


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = (IsAdminUserOrIsAuthenticatedReadOnly,)



class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.select_related("airplane_type")
    permission_classes = (IsAdminUserOrIsAuthenticatedReadOnly,)


    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return AirplaneListSerializer
        return AirplaneSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.select_related("source", "destination")
    permission_classes = (IsAdminUserOrIsAuthenticatedReadOnly,)


    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        if self.action == "retrieve":
            return RouteDetailSerializer
        return RouteSerializer


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.select_related(
        "route",
        "route__source",
        "route__destination",
        "airplane",
        "airplane__airplane_type")

    def get_queryset(self):
        queryset = self.queryset

        source = self.request.query_params.get("source")
        destination = self.request.query_params.get("destination")
        departure_time = self.request.query_params.get("departure_time")
        arrival_time = self.request.query_params.get("arrival_time")

        if source:
            queryset = queryset.filter(
                Q(route__source__name__icontains=source) |
                Q(route__source__closest_big_city__icontains=source))

        if destination:
            queryset = queryset.filter(
                Q(route__destination__name__icontains=destination) |
                Q(route__destination__closest_big_city__icontains=destination))

        if departure_time:
            queryset = queryset.filter(departure_time__date=departure_time)

        if arrival_time:
            queryset = queryset.filter(arrival_time__date=arrival_time)

        if self.action == "list":
            queryset = queryset.annotate(
                available_seats=(F("airplane__rows") * F("airplane__seats_in_row")) - Count("tickets")).order_by("id")
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        if self.action == "retrieve":
            return FlightDetailSerializer
        return FlightSerializer


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.prefetch_related(
        Prefetch(
            "flights",
            queryset=Flight.objects.select_related(
                "route__source",
                "route__destination"
            )
        )
    )
    serializer_class = CrewSerializer
    permission_classes = (IsAdminUserOrIsAuthenticatedReadOnly,)


    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return CrewListSerializer
        return CrewSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related(
        Prefetch(
            "tickets",
            queryset=Ticket.objects.select_related(
                "flight__route__destination",
                "flight__route__source"
            )
        )
    )
    permission_classes = (IsAdminUserOrIsAuthenticatedReadOnly,)


    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return OrderListSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)