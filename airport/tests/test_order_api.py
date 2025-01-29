import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from airport.models import Flight, Order, Ticket
from airport.serializers import (
    OrderListSerializer,
    OrderRetrieveSerializer,
)
from airport.tests.test_airplane_api import sample_airplane
from airport.tests.test_crew_api import sample_crew
from airport.tests.test_flight_api import sample_flight
from airport.tests.test_route_api import sample_route

# Create your tests here.
ORDER_URL = reverse("airport:orders-list")


def sample_ticket(**params) -> Ticket:
    """Create and return a sample ticket"""
    flight = sample_flight()
    defaults = {
        "row": 1,
        "seat": 1,
        "flight": flight,
        "order": None,
    }
    defaults.update(params)
    return Ticket.objects.create(**defaults)


class UnauthorizedOrderApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(ORDER_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedFlightApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test", password="TESTPASSWORD"
        )
        self.client.force_authenticate(self.user)

    def sample_order(self, **params) -> Order:
        """Create and return a sample order"""
        defaults = {
            "user": self.user,
            "created_at": datetime.datetime.now(),
        }
        defaults.update(params)
        return Order.objects.create(**defaults)

    def test_order_list(self):
        order1 = self.sample_order()
        sample_ticket(order=order1)
        order2 = self.sample_order()
        sample_ticket(order=order2)
        print(order1.tickets.all(), order2.tickets.all())

        orders = Order.objects.all().order_by("-created_at")
        res = self.client.get(ORDER_URL)
        serializer = OrderListSerializer(orders, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            res.data["results"],
            serializer.data,
        )

    def test_retrieve_order_detail(self):
        order = self.sample_order()
        sample_ticket(order=order)
        serializer = OrderRetrieveSerializer(order)

        res = self.client.get(
            reverse("airport:orders-detail", args=[order.id])
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
        res = self.client.post(ORDER_URL, payload)

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
        res = self.client.post(ORDER_URL, payload)
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
