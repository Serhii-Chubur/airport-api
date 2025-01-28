from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

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
                                 FlightRetrieveSerializer,
                                 AirplaneImageSerializer, )


# Create your views here.
class ViewsSetPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 10


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    pagination_class = ViewsSetPagination
    permission_classes = ()

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

        return self.queryset


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    pagination_class = ViewsSetPagination

    def get_serializer_class(self):
        if self.action == "retrieve":
            return AirplaneTypeRetrieveSerializer

        return AirplaneTypeSerializer


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    pagination_class = ViewsSetPagination

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
    pagination_class = ViewsSetPagination


def str_to_int(id_string):
    return [int(num) for num in id_string.split(",")]


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all().select_related("source", "destination", )
    pagination_class = ViewsSetPagination

    def get_serializer_class(self):

        if self.action == "retrieve":
            return RouteRetrieveSerializer

        return RouteSerializer

    def get_queryset(self):
        source = self.request.GET.get("source")
        destination = self.request.GET.get("destination")

        if source:
            self.queryset = self.queryset.filter(
                source_id__in=str_to_int(source)
            )

        if destination:
            self.queryset = self.queryset.filter(
                destination_id__in=str_to_int(destination)
            )

        if self.action == "list":
            return self.queryset.prefetch_related(
                "destination", "source")

        return self.queryset


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    pagination_class = ViewsSetPagination

    def get_serializer_class(self):

        if self.action == "retrieve":
            return AirplaneRetrieveSerializer

        if self.action == "upload_image":
            return AirplaneImageSerializer

        return AirplaneSerializer

    def get_queryset(self):
        airplane_type = self.request.GET.get("type")

        if airplane_type:
            self.queryset = self.queryset.filter(
                airplane_type_id__in=str_to_int(airplane_type)
            )

        if self.action == "list":
            return self.queryset.prefetch_related("airplane_type")

        if self.action == "retrieve":
            return self.queryset.prefetch_related(
                "flights__route__destination",
                "flights__route__source").select_related("airplane_type")

        return self.queryset

    @action(
        methods=["POST", "GET"],
        detail=True,
        url_path="upload-image",
        permission_classes=(IsAdminUser,))
    def upload_image(self, request, *args, **kwargs):
        airplane = self.get_object()
        serializer = self.get_serializer(airplane, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data, status=status.HTTP_200_OK
            )
        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all().select_related(
        "route__destination", "route__source", "airplane"
    )
    pagination_class = ViewsSetPagination

    def get_serializer_class(self):
        if self.action == "retrieve":
            return FlightRetrieveSerializer
        return FlightSerializer

    def get_queryset(self):
        route = self.request.GET.get("route")
        airplane = self.request.GET.get("airplane")
        crew = self.request.GET.get("crew")

        if route:
            self.queryset = self.queryset.filter(
                route_id__in=str_to_int(route)
            )

        if airplane:
            self.queryset = self.queryset.filter(
                airplane_id__in=str_to_int(airplane)
            )

        if crew:
            self.queryset = self.queryset.filter(
                crew__in=str_to_int(crew)
            )

        if self.action == "list":
            return self.queryset

        return self.queryset.select_related("airplane__airplane_type")
