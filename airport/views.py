from rest_framework import viewsets

from airport.models import (AirplaneType,
                            Order,
                            Flight,
                            Airplane,
                            Route,
                            Airport,
                            Crew)
from airport.serializers import (AirplaneTypeSerializer,
                                 OrderListSerializer,
                                 OrderRetrieveSerializer,
                                 CrewListSerializer,
                                 AirportSerializer,
                                 RouteSerializer,
                                 AirplaneSerializer,
                                 FlightSerializer,
                                 AirplaneTypeRetrieveSerializer,
                                 CrewRetrieveSerializer,
                                 RouteRetrieveSerializer,
                                 AirplaneRetrieveSerializer,
                                 FlightRetrieveSerializer, )


# Create your views here.
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return OrderRetrieveSerializer
        return OrderListSerializer

    def get_queryset(self):
        if self.action == "list":
            return self.queryset.filter(
                user=self.request.user
            ).prefetch_related("tickets")
        if self.action == "retrieve":
            return self.queryset.filter(
                user=self.request.user
            ).prefetch_related("tickets__flight__route")


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return AirplaneTypeRetrieveSerializer
        return AirplaneTypeSerializer


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CrewRetrieveSerializer
        return CrewListSerializer

    def get_queryset(self):
        if self.action == "retrieve":
            return self.queryset.prefetch_related(
                "flights__airplane__airplane_type",
                "flights__route__destination",
                "flights__route__source"
            )
        return self.queryset


class AirportViewSet(viewsets.ModelViewSet):
    serializer_class = AirportSerializer
    queryset = Airport.objects.all()


class RouteViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self):
        if self.action == "retrieve":
            return RouteRetrieveSerializer
        return RouteSerializer

    queryset = Route.objects.all()

    def get_queryset(self):
        if self.action == "list":
            return self.queryset.prefetch_related("source", "destination")
        return self.queryset


class AirplaneViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self):
        if self.action == "retrieve":
            return AirplaneRetrieveSerializer
        return AirplaneSerializer

    queryset = Airplane.objects.all().select_related("airplane_type")


class FlightViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self):
        if self.action == "retrieve":
            return FlightRetrieveSerializer
        return FlightSerializer

    queryset = Flight.objects.all().select_related(
        "route__source", "route__destination"
    )
