from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from airport.models import (
    AirplaneType,
    Order,
    Flight,
    Airplane,
    Route,
    Airport,
    Crew,
)
from airport.parameters import (
    airplane_type_parameters,
    flight_parameters,
    route_parameters,
)
from airport.serializers import (
    AirplaneTypeSerializer,
    OrderListSerializer,
    OrderRetrieveSerializer,
    CrewListSerializer,
    AirportSerializer,
    RouteListSerializer,
    AirplaneSerializer,
    FlightSerializer,
    AirplaneTypeRetrieveSerializer,
    CrewRetrieveSerializer,
    RouteRetrieveSerializer,
    AirplaneRetrieveSerializer,
    FlightRetrieveSerializer,
    AirplaneImageSerializer,
    RouteSerializer,
    AirplaneListSerializer,
    FlightListSerializer,
)


# Create your views here.
class ViewsSetPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 10


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by("-created_at")
    pagination_class = ViewsSetPagination
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):

        if self.action == "retrieve":
            return OrderRetrieveSerializer

        return OrderListSerializer

    def get_queryset(self):

        if self.request.user.id:
            if self.action == "list":
                return self.queryset.filter(
                    user=self.request.user
                ).prefetch_related("tickets")

            if self.action == "retrieve":
                return self.queryset.filter(
                    user=self.request.user
                ).prefetch_related("tickets__flight__route")

            return self.queryset
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    @extend_schema()
    def list(self, request, *args, **kwargs):
        """Get all orders."""
        return super().list(request, *args, **kwargs)

    @extend_schema(responses=OrderRetrieveSerializer)
    def retrieve(self, request, *args, **kwargs):
        """Get order by id."""
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(methods=["POST"])
    def create(self, request, *args, **kwargs):
        """Create an order."""
        return super().create(request, *args, **kwargs)

    @extend_schema(methods=["PUT"])
    def update(self, request, *args, **kwargs):
        """Update an order with provided id."""
        return super().update(request, *args, **kwargs)

    @extend_schema(methods=["PATCH"])
    def partial_update(self, request, *args, **kwargs):
        """Update an order with provided id."""
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(methods=["DELETE"])
    def destroy(self, request, *args, **kwargs):
        """Delete order with provided id."""
        return super().destroy(request, *args, **kwargs)


class AirplaneTypeViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = AirplaneType.objects.all().order_by("name")
    pagination_class = ViewsSetPagination

    @extend_schema(responses=AirplaneTypeSerializer)
    def list(self, request, *args, **kwargs):
        """Get all airplane types."""
        return super().list(request, *args, **kwargs)

    @extend_schema(methods=["POST"], responses=AirplaneTypeSerializer)
    def create(self, request, *args, **kwargs):
        """Create an airplane type."""
        return super().create(request, *args, **kwargs)

    @extend_schema(responses=AirplaneTypeRetrieveSerializer)
    def retrieve(self, request, *args, **kwargs):
        """Get airplane type by id."""
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(methods=["PUT"], responses=AirplaneTypeSerializer)
    def update(self, request, *args, **kwargs):
        """Update airplane type with provided id."""
        return super().update(request, *args, **kwargs)

    @extend_schema(methods=["PATCH"], responses=AirplaneTypeSerializer)
    def partial_update(self, request, *args, **kwargs):
        """Update airplane type with provided id."""
        return super().partial_update(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return AirplaneTypeRetrieveSerializer

        return AirplaneTypeSerializer


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all().order_by("first_name")
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
                "flights__route__source",
            )

        return self.queryset

    @extend_schema()
    def list(self, request, *args, **kwargs):
        """Get all crews."""
        return super().list(request, *args, **kwargs)

    @extend_schema()
    def retrieve(self, request, *args, **kwargs):
        """Get crew by id."""
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(methods=["POST"])
    def create(self, request, *args, **kwargs):
        """Create a crew."""
        return super().create(request, *args, **kwargs)

    @extend_schema(methods=["PUT"])
    def update(self, request, *args, **kwargs):
        """Update crew with provided id."""
        return super().update(request, *args, **kwargs)

    @extend_schema(methods=["PATCH"])
    def partial_update(self, request, *args, **kwargs):
        """Update crew with provided id."""
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(methods=["DELETE"])
    def destroy(self, request, *args, **kwargs):
        """Delete crew with provided id."""
        return super().destroy(request, *args, **kwargs)


class AirportViewSet(viewsets.ModelViewSet):
    serializer_class = AirportSerializer
    queryset = Airport.objects.all().order_by("name")
    pagination_class = ViewsSetPagination

    @extend_schema()
    def list(self, request, *args, **kwargs):
        """Get all airports."""
        return super().list(request, *args, **kwargs)

    @extend_schema()
    def retrieve(self, request, *args, **kwargs):
        """Get airport by id."""
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(methods=["POST"])
    def create(self, request, *args, **kwargs):
        """Create an airport."""
        return super().create(request, *args, **kwargs)

    @extend_schema(methods=["PUT"])
    def update(self, request, *args, **kwargs):
        """Update airport with provided id."""
        return super().update(request, *args, **kwargs)

    @extend_schema(methods=["PATCH"])
    def partial_update(self, request, *args, **kwargs):
        """Update airport with provided id."""
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(methods=["DELETE"])
    def destroy(self, request, *args, **kwargs):
        """Delete airport with provided id."""
        return super().destroy(request, *args, **kwargs)


def str_to_int(id_string):
    return [int(num) for num in id_string.split(",")]


class RouteViewSet(viewsets.ModelViewSet):
    queryset = (
        Route.objects.all()
        .select_related(
            "source",
            "destination",
        )
        .order_by("source__name")
    )
    pagination_class = ViewsSetPagination

    @extend_schema(responses=RouteListSerializer, parameters=route_parameters)
    def list(self, request, *args, **kwargs):
        """Get all routes. Filtering by source, destination."""
        return super().list(request, *args, **kwargs)

    @extend_schema(responses=RouteRetrieveSerializer)
    def retrieve(self, request, *args, **kwargs):
        """Get route by id."""
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(methods=["POST"], responses=RouteSerializer)
    def create(self, request, *args, **kwargs):
        """Create a route."""
        return super().create(request, *args, **kwargs)

    @extend_schema(methods=["PUT"], responses=RouteSerializer)
    def update(self, request, *args, **kwargs):
        """Update a route with provided id."""
        return super().update(request, *args, **kwargs)

    @extend_schema(methods=["PATCH"], responses=RouteSerializer)
    def partial_update(self, request, *args, **kwargs):
        """Update a route with provided id."""
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(methods=["DELETE"], responses=RouteSerializer)
    def destroy(self, request, *args, **kwargs):
        """Delete route with provided id."""
        return super().destroy(request, *args, **kwargs)

    def get_serializer_class(self):

        if self.action == "retrieve":
            return RouteRetrieveSerializer

        return RouteListSerializer

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
            return self.queryset.prefetch_related("destination", "source")

        return self.queryset


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all().order_by("-name")
    pagination_class = ViewsSetPagination

    @extend_schema(
        responses=AirplaneSerializer, parameters=airplane_type_parameters
    )
    def list(self, request, *args, **kwargs):
        """Get all airplanes. Filtering by airplane type"""
        return super().list(request, *args, **kwargs)

    @extend_schema(responses=AirplaneRetrieveSerializer)
    def retrieve(self, request, *args, **kwargs):
        """Get airplane by id."""
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(methods=["POST"], responses=AirplaneSerializer)
    def create(self, request, *args, **kwargs):
        """Create an airplane."""
        return super().create(request, *args, **kwargs)

    @extend_schema(methods=["PUT"], responses=AirplaneSerializer)
    def update(self, request, *args, **kwargs):
        """Update an airplane with provided id."""
        return super().update(request, *args, **kwargs)

    @extend_schema(methods=["PATCH"], responses=AirplaneSerializer)
    def partial_update(self, request, *args, **kwargs):
        """Update an airplane with provided id."""
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(methods=["DELETE"], responses=AirplaneSerializer)
    def destroy(self, request, *args, **kwargs):
        """Delete airplane with provided id."""
        return super().destroy(request, *args, **kwargs)

    def get_serializer_class(self):

        if self.action == "retrieve":
            return AirplaneRetrieveSerializer

        if self.action == "upload_image":
            return AirplaneImageSerializer

        if self.action in ("create", "update", "list", "partial_update"):
            return AirplaneListSerializer

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
                "flights__route__destination", "flights__route__source"
            ).select_related("airplane_type")

        return self.queryset

    @action(
        methods=["POST", "GET"],
        detail=True,
        url_path="upload-image",
        permission_classes=(IsAdminUser,),
    )
    def upload_image(self, request, *args, **kwargs):
        """Add/update image of airplane instance."""
        airplane = self.get_object()
        serializer = self.get_serializer(airplane, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FlightViewSet(viewsets.ModelViewSet):
    queryset = (
        Flight.objects.all()
        .select_related("route__destination", "route__source", "airplane")
        .order_by("departure_time")
    )
    pagination_class = ViewsSetPagination

    @extend_schema(responses=FlightSerializer, parameters=flight_parameters)
    def list(self, request, *args, **kwargs):
        """Get all flights. Filtering by airplane, route, crew"""
        return super().list(request, *args, **kwargs)

    @extend_schema(responses=FlightRetrieveSerializer)
    def retrieve(self, request, *args, **kwargs):
        """Get flight by id."""
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(methods=["POST"], responses=FlightSerializer)
    def create(self, request, *args, **kwargs):
        """Create a flight."""
        return super().create(request, *args, **kwargs)

    @extend_schema(methods=["PUT"], responses=FlightSerializer)
    def update(self, request, *args, **kwargs):
        """Update a flight with provided id."""
        return super().update(request, *args, **kwargs)

    @extend_schema(methods=["PATCH"], responses=FlightSerializer)
    def partial_update(self, request, *args, **kwargs):
        """Update a flight with provided id."""
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(methods=["DELETE"], responses=FlightSerializer)
    def destroy(self, request, *args, **kwargs):
        """Delete flight with provided id."""
        return super().destroy(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return FlightRetrieveSerializer

        if self.action in ("create", "update", "list", "partial_update"):
            return FlightListSerializer
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
            self.queryset = self.queryset.filter(crew__in=str_to_int(crew))

        if self.action == "list":
            return self.queryset

        return self.queryset.select_related("airplane__airplane_type")
