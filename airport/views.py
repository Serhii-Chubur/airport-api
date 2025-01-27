from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

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


class AirportSetPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 10


class AirportViewSet(viewsets.ModelViewSet):
    serializer_class = AirportSerializer
    queryset = Airport.objects.all()
    pagination_class = AirportSetPagination


class RouteViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self):
        if self.action == "retrieve":
            return RouteRetrieveSerializer
        return RouteSerializer

    queryset = Route.objects.all().select_related("source", "destination", )

    def get_queryset(self):
        if self.action == "list":
            return self.queryset.prefetch_related(
                "destination", "source")
        return self.queryset


class AirplaneViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self):
        if self.action == "retrieve":
            return AirplaneRetrieveSerializer
        return AirplaneSerializer

    queryset = Airplane.objects.all()

    def get_queryset(self):
        if self.action == "list":
            return self.queryset.prefetch_related("airplane_type")
        if self.action == "retrieve":
            return self.queryset.prefetch_related(
                "flights__route__destination",
                "flights__route__source").select_related("airplane_type")
        return self.queryset


class FlightViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self):
        if self.action == "retrieve":
            return FlightRetrieveSerializer
        return FlightSerializer

    queryset = Flight.objects.all().select_related(
        "route__destination", "route__source", "airplane"
    )

    def get_queryset(self):
        if self.action == "list":
            return self.queryset
        return self.queryset.select_related("airplane__airplane_type")
