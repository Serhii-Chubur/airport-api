import pathlib
import uuid

from django.conf import settings
from django.db import models
from django.utils.text import slugify
from rest_framework.exceptions import ValidationError


# 8 models
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
        Airport, on_delete=models.CASCADE, related_name="source_airport"
    )
    destination = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="destination_airport"
    )
    distance = models.IntegerField()

    def __str__(self):
        return f"{self.source} - {self.destination}"


def image_upload(instance: "Airplane", filename: str) -> pathlib.Path:
    filename = (
            f"{slugify(instance.__str__())}"
            f"_{uuid.uuid4()}"
            + pathlib.Path(filename).suffix
    )
    return pathlib.Path("upload/airplanes") / pathlib.Path(filename)


class Airplane(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(
        AirplaneType, on_delete=models.CASCADE, related_name="airplanes"
    )
    image = models.ImageField(upload_to=image_upload, blank=True, null=True)

    def __str__(self):
        return f"{self.airplane_type} {self.name}"


class Flight(models.Model):
    route = models.ForeignKey(
        Route, on_delete=models.CASCADE, related_name="flights"
    )
    airplane = models.ForeignKey(
        Airplane, on_delete=models.CASCADE, related_name="flights"
    )
    crew = models.ManyToManyField(
        Crew, related_name="flights"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    def __str__(self):
        return (f"{self.route}, "
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
    def validate_ticket(
            seat: int, row: int, num_seats: int, num_rows: int, error
    ):
        if not 1 <= seat <= num_seats or not 1 <= row <= num_rows:
            raise error

    def clean(self):
        Ticket.validate_ticket(
            self.seat,
            self.row,
            self.flight.airplane.seats_in_row,
            self.flight.airplane.rows,
            ValidationError("Invalid seat number")
        )

    def __str__(self):
        return f"{self.flight.route}, row: {self.row}, seat: {self.seat}"
