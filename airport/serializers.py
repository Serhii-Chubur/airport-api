from rest_framework import serializers

from airport.models import (AirplaneType,
                            Order,
                            Crew,
                            Airport,
                            Route,
                            Airplane,
                            Flight,
                            Ticket)


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = "__all__"


class AirplaneTypeRetrieveSerializer(AirplaneTypeSerializer):
    airplanes = serializers.SlugRelatedField(
        slug_field="name", read_only=True, many=True
    )


class CrewSerializer(serializers.ModelSerializer):
    full_name = serializers.StringRelatedField(source="__str__")

    class Meta:
        model = Crew
        fields = ("id", "full_name",)


class FlightForCrewRetrieveSerializer(serializers.ModelSerializer):
    route = serializers.StringRelatedField(source="route.__str__")
    airplane = serializers.StringRelatedField(source="airplane.__str__")

    class Meta:
        model = Flight
        fields = "route", "departure_time", "arrival_time", "airplane"


class CrewRetrieveSerializer(serializers.ModelSerializer):
    flights = FlightForCrewRetrieveSerializer(many=True, read_only=True)

    class Meta:
        model = Crew
        fields = "id", "first_name", "last_name", "flights",


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = "__all__"


class RouteSerializer(serializers.ModelSerializer):
    source = serializers.SlugRelatedField(
        slug_field="name", read_only=True
    )
    destination = serializers.SlugRelatedField(
        slug_field="name", read_only=True
    )

    class Meta:
        model = Route
        fields = "__all__"


class RouteRetrieveSerializer(serializers.ModelSerializer):
    source = AirportSerializer()
    destination = AirportSerializer()
    flights = serializers.StringRelatedField(many=True)

    class Meta:
        model = Route
        fields = "__all__"


class AirplaneSerializer(serializers.ModelSerializer):
    name = serializers.StringRelatedField(source="__str__")

    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row")


class AirplaneRetrieveSerializer(AirplaneSerializer):
    flights = serializers.StringRelatedField(many=True)

    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row", "flights")


class FlightSerializer(serializers.ModelSerializer):
    route = serializers.StringRelatedField(source="route.__str__")

    class Meta:
        model = Flight
        fields = "id", "route"


class FlightRetrieveSerializer(serializers.ModelSerializer):
    route = serializers.StringRelatedField(source="route.__str__")
    airplane = serializers.StringRelatedField(source="airplane.__str__")
    crew = serializers.StringRelatedField(source="crew.__str__")

    class Meta:
        model = Flight
        fields = "__all__"


class TicketRetrieveSerializer(serializers.ModelSerializer):
    flight = serializers.StringRelatedField(source="flight.__str__")

    class Meta:
        model = Ticket
        fields = "id", "flight", "row", "seat"


class TicketListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = "id", "row", "seat"


class OrderListSerializer(serializers.ModelSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = "id", "created_at", "tickets"


class OrderRetrieveSerializer(OrderListSerializer):
    tickets = TicketRetrieveSerializer(many=True, read_only=True)
