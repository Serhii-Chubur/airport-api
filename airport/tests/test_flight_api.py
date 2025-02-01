from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from airport.models import Flight
from airport.serializers import (
    FlightListSerializer,
    FlightRetrieveSerializer,
)
from airport.tests.test_airplane_api import sample_airplane
from airport.tests.test_crew_api import sample_crew
from airport.tests.test_route_api import sample_route

# Create your tests here.
FLIGHT_URL = reverse("airport:flights-list")


def sample_flight(**params) -> Flight:
    """Create and return a sample flight"""
    route = sample_route()
    airplane = sample_airplane()
    crew = sample_crew()
    departure_time = params.get("departure_time", "2023-01-01T00:00:00Z")
    arrival_time = params.get("arrival_time", "2023-01-01T00:00:00Z")
    defaults = {
        "route": route,
        "airplane": airplane,
        "departure_time": departure_time,
        "arrival_time": arrival_time,
    }
    defaults.update(params)
    flight = Flight.objects.create(**defaults)
    flight.crew.add(crew)
    return flight


class UnauthorizedFlightApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(FLIGHT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedFlightApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test", password="TESTPASSWORD"
        )
        self.client.force_authenticate(self.user)

    def test_flight_list(self):
        sample_flight()
        route = sample_route(distance=200)
        sample_flight(route=route)

        flights = Flight.objects.all()
        res = self.client.get(FLIGHT_URL)
        serializer = FlightListSerializer(flights, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            res.data["results"],
            serializer.data,
        )

    def test_flight_list_filter_by_route(self):
        flight1 = sample_flight()
        route = sample_route()
        flight2 = sample_flight(route=route)

        serializer1 = FlightListSerializer(flight1)
        serializer2 = FlightListSerializer(flight2)

        res = self.client.get(FLIGHT_URL, {"route": route.id})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer2.data, res.data["results"])
        self.assertNotIn(serializer1.data, res.data["results"])

    def test_flight_list_filter_by_airplane(self):
        flight1 = sample_flight()
        airplane = sample_airplane()
        flight2 = sample_flight(airplane=airplane)

        serializer1 = FlightListSerializer(flight1)
        serializer2 = FlightListSerializer(flight2)

        res = self.client.get(FLIGHT_URL, {"airplane": airplane.id})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer2.data, res.data["results"])
        self.assertNotIn(serializer1.data, res.data["results"])

    def test_flight_list_filter_by_crew(self):
        flight1 = sample_flight()
        crew = sample_crew(first_name="John", last_name="Doe")
        flight2 = sample_flight()
        flight2.crew.all().delete()
        flight2.crew.add(crew)

        serializer1 = FlightListSerializer(flight1)
        serializer2 = FlightListSerializer(flight2)

        res = self.client.get(FLIGHT_URL, {"crew": crew.id})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer2.data, res.data["results"])
        self.assertNotIn(serializer1.data, res.data["results"])

    def test_retrieve_flight_detail(self):
        flight = sample_flight()
        serializer = FlightRetrieveSerializer(flight)

        res = self.client.get(
            reverse("airport:flights-detail", args=[flight.id])
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_flight_forbidden(self):
        route = sample_route()
        airplane = sample_airplane()
        departure_time = "2024-01-01T00:00:00Z"
        arrival_time = "2024-01-01T00:00:00Z"
        payload = {
            "route": route,
            "airplane": airplane,
            "crew": [sample_crew().id],
            "departure_time": departure_time,
            "arrival_time": arrival_time,
        }
        res = self.client.post(FLIGHT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminUserFlightApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test", password="TESTPASSWORD", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_flight(self):
        route = sample_route()
        airplane = sample_airplane()
        departure_time = "2024-01-01T00:00:00+00:00"
        arrival_time = "2024-01-01T00:00:00+00:00"
        payload = {
            "route": route.id,
            "airplane": airplane.id,
            "crew": [sample_crew().id],
            "departure_time": departure_time,
            "arrival_time": arrival_time,
        }
        res = self.client.post(FLIGHT_URL, payload)
        flights = Flight.objects.all()
        flight = Flight.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(flights.count(), 1)
        self.assertEqual(flight.route.id, payload["route"])
        self.assertEqual(flight.airplane.id, payload["airplane"])
        self.assertEqual(
            flight.departure_time.isoformat(), payload["departure_time"]
        )
        self.assertEqual(
            flight.arrival_time.isoformat(), payload["arrival_time"]
        )

    def test_delete_flight(self):
        flight = sample_flight()
        res = self.client.delete(
            reverse("airport:flights-detail", args=[flight.id])
        )

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
