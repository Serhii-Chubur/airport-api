from django.db import transaction
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


class CrewListSerializer(serializers.ModelSerializer):
    full_name = serializers.StringRelatedField(source="__str__")
    first_name = serializers.CharField(required=True, write_only=True)
    last_name = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = Crew
        fields = ("id", "full_name", "first_name", "last_name")


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
    source = serializers.ChoiceField(
        choices=Airport.objects.values_list("name", flat=True)
    )
    destination = serializers.ChoiceField(
        choices=Airport.objects.values_list("name", flat=True)
    )

    class Meta:
        model = Route
        fields = "__all__"

    def create(self, validated_data):
        source = validated_data.pop("source")
        destination = validated_data.pop("destination")
        return Route.objects.create(
            source=Airport.objects.get(name=source),
            destination=Airport.objects.get(name=destination),
            **validated_data
        )

    def update(self, instance, validated_data):
        source_name = validated_data.get("source", instance.source.name)
        destination_name = validated_data.get(
            "destination", instance.destination.name
        )

        source = Airport.objects.get(
            name=source_name
        )
        destination = Airport.objects.get(
            name=destination_name
        )

        instance.source = source
        instance.destination = destination

        instance.distance = validated_data.get(
            "distance", instance.distance
        )
        instance.save()
        return instance


class RouteRetrieveSerializer(serializers.ModelSerializer):
    source = AirportSerializer()
    destination = AirportSerializer()
    flights = serializers.StringRelatedField(many=True)

    class Meta:
        model = Route
        fields = "__all__"


class AirplaneSerializer(serializers.ModelSerializer):
    name = serializers.StringRelatedField(source="__str__")
    airplane_type = serializers.ChoiceField(
        choices=AirplaneType.objects.all(), write_only=True
    )

    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row", "airplane_type")


class AirplaneRetrieveSerializer(AirplaneSerializer):
    flights = serializers.StringRelatedField(many=True)

    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row", "flights")


class FlightSerializer(serializers.ModelSerializer):
    air_lane = serializers.CharField(
        source="route.__str__", read_only=True
    )
    route = serializers.ChoiceField(
        choices=Route.objects.all(), write_only=True
    )
    crew = serializers.MultipleChoiceField(
        choices=Crew.objects.all(), write_only=True
    )
    airplane = serializers.ChoiceField(
        choices=Airplane.objects.all(), write_only=True
    )
    departure_time = serializers.DateTimeField(write_only=True)
    arrival_time = serializers.DateTimeField(write_only=True)

    class Meta:
        model = Flight
        fields = "__all__"


class FlightRetrieveSerializer(serializers.ModelSerializer):
    route = serializers.CharField(source="route.__str__")
    airplane = serializers.CharField(source="airplane.__str__")
    crew = serializers.StringRelatedField(many=True)

    class Meta:
        model = Flight
        fields = "__all__"


class TicketListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = "id", "row", "seat", "flight"

    def validate(self, attrs):
        Ticket.validate_ticket(
            attrs["seat"],
            attrs["row"],
            attrs["flight"].airplane.seats_in_row,
            attrs["flight"].airplane.rows,
            serializers.ValidationError("Invalid seat number")
        )


class TicketRetrieveSerializer(TicketListSerializer):
    flight = serializers.StringRelatedField(source="flight.__str__")


class OrderListSerializer(serializers.ModelSerializer):
    tickets = TicketListSerializer(many=True)

    class Meta:
        model = Order
        fields = "id", "created_at", "tickets"

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket in tickets_data:
                Ticket.objects.create(order=order, **ticket)
            return order


class OrderRetrieveSerializer(OrderListSerializer):
    tickets = TicketRetrieveSerializer(many=True, read_only=True)
