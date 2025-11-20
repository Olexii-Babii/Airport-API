from django.shortcuts import render
from rest_framework import viewsets

from airport.models import Airport, AirplaneType
from airport.serializers import (
    AirportSerializer,
    AirplaneTypeSerializer
)


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
