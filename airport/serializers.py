from rest_framework import serializers

from airport.models import AirplaneType, Order, Crew, Airport, Route, Airplane, Flight, Ticket


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = "__all__"


class CrewSerializer(serializers.ModelSerializer):
    full_name = serializers.StringRelatedField(source="__str__")

    class Meta:
        model = Crew
        fields = ("id", "full_name",)


class AirportSerializer(serializers.ModelSerializer):

    class Meta:
        model = Airport
        fields = "__all__"


class RouteSerializer(serializers.ModelSerializer):
    source = serializers.SlugRelatedField(slug_field="name", read_only=True)
    destination = serializers.SlugRelatedField(slug_field="name", read_only=True)

    class Meta:
        model = Route
        fields = "__all__"


class AirplaneSerializer(serializers.ModelSerializer):
    name = serializers.StringRelatedField(source="__str__")

    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row")


class FlightSerializer(serializers.ModelSerializer):
    route = serializers.StringRelatedField(source="route.__str__")
    airplane = serializers.StringRelatedField(source="airplane.__str__")

    class Meta:
        model = Flight
        fields = "__all__"


class TicketSerializer(serializers.ModelSerializer):
    flight = serializers.StringRelatedField(source="flight.__str__")
    order = serializers.SlugRelatedField(slug_field="created_at", read_only=True)

    class Meta:
        model = Ticket
        fields = "__all__"
