from django.conf import settings
from django.db import models
from rest_framework.exceptions import ValidationError


# Create your models here.
class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    def __str__(self):
        return f"Order {self.created_at} by {self.user}"


class AirplaneType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Airport(models.Model):
    name = models.CharField(max_length=255)
    closest_big_city = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Route(models.Model):
    source = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="routes"
    )
    destination = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="routes"
    )
    distance = models.IntegerField()

    def __str__(self):
        return f"{self.source} - {self.destination}, {self.distance} km"


class Airplane(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(
        AirplaneType, on_delete=models.CASCADE, related_name="airplanes"
    )

    def __str__(self):
        return self.name


class Flight(models.Model):
    route = models.ForeignKey(
        Route, on_delete=models.CASCADE, related_name="flights"
    )
    airplane = models.ForeignKey(
        Airplane, on_delete=models.CASCADE, related_name="flights"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    def __str__(self):
        return (f"{self.airplane}, {self.route}, "
                f"departure: {self.departure_time}, "
                f"arrival: {self.arrival_time}")


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(
        Flight, on_delete=models.CASCADE, related_name="tickets"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="tickets"
    )

    class Meta:
        unique_together = ("flight", "row", "seat")

    @staticmethod
    def validate_ticket(seat: int, num_seats: int, error):
        if not 1 <= seat <= num_seats:
            raise error

    def clean(self):
        Ticket.validate_ticket(
            self.seat,
            self.flight.airplane.seats_in_row,
            ValidationError("Invalid seat number")
        )

    def __str__(self):
        return f"{self.flight.route}, row: {self.row}, seat: {self.seat}"
