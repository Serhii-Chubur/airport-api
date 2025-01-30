from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from airport.models import Order, Ticket
from airport.serializers import (
    OrderListSerializer,
    OrderRetrieveSerializer,
)
from airport.tests.test_flight_api import sample_flight

# Create your tests here.
ORDER_URL = reverse("airport:orders-list")


class UnauthorizedOrderApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(ORDER_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class OrderApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.flight = sample_flight()
        self.user = get_user_model().objects.create_user(
            email="test@test.test", password="TESTPASSWORD"
        )
        self.client.force_authenticate(self.user)
        self.order = Order.objects.create(user=self.user)
        self.ticket = Ticket.objects.create(
            flight=self.flight, row=2, seat=1, order=self.order
        )

    def test_get_order_list(self):
        res = self.client.get(ORDER_URL)
        order = res.data["results"][0]
        serializer = OrderListSerializer(order)
        ticket = order["tickets"][0]
        flight = ticket["flight"]

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"][0], serializer.data)
        self.assertEqual(res.data["count"], 1)
        self.assertEqual(len(order["tickets"]), 1)
        self.assertEqual(ticket["row"], 2)
        self.assertEqual(ticket["seat"], 1)
        self.assertEqual(
            flight,
            "TestSource - TestDestination, departure: 2023-01-01 "
            "00:00:00+00:00, arrival: 2023-01-01 00:00:00+00:00",
        )

    def test_get_order_detail(self):
        res = self.client.get(reverse("airport:orders-detail", args=[1]))
        order = Order.objects.get(id=1)
        serializer = OrderRetrieveSerializer(order)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        flight_info = list(res.data["tickets"][0]["flight"].keys())
        self.assertEqual(flight_info[1], "route")
        self.assertEqual(flight_info[2], "airplane")
        self.assertEqual(flight_info[3], "crew")
