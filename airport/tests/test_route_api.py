from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from airport.models import Route, Airport
from airport.serializers import (
    RouteListSerializer,
    RouteRetrieveSerializer,
)

# Create your tests here.
ROUTE_URL = reverse("airport:routes-list")


def sample_airport(**params) -> Airport:
    """Create and return a sample airport"""
    defaults = {
        "name": "TestAirport",
        "closest_big_city": "TestBigCity",
    }
    defaults.update(params)
    return Airport.objects.create(**defaults)


def sample_route(**params) -> Route:
    """Create and return a sample crew"""
    distance = params.get("distance", 100)
    source = sample_airport(
        name="TestSource", closest_big_city="TestSourceCity"
    )
    destination = sample_airport(
        name="TestDestination", closest_big_city="TestDestinationCity"
    )
    defaults = {
        "source": source,
        "destination": destination,
        "distance": distance,
    }
    defaults.update(params)
    return Route.objects.create(**defaults)


class UnauthorizedRouteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(ROUTE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedRouteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test", password="TESTPASSWORD"
        )
        self.client.force_authenticate(self.user)

    def test_route_list(self):
        sample_route()
        sample_route(distance=200)

        routes = Route.objects.all()
        res = self.client.get(ROUTE_URL)
        serializer = RouteListSerializer(routes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_route_list_filter_by_source(self):
        route1 = sample_route()
        source = sample_airport()
        route2 = sample_route(source=source)

        serializer1 = RouteListSerializer(route1)
        serializer2 = RouteListSerializer(route2)

        res = self.client.get(ROUTE_URL, {"source": source.id})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer2.data, res.data["results"])
        self.assertNotIn(serializer1.data, res.data["results"])

    def test_route_list_filter_by_destination(self):
        route1 = sample_route()
        destination = sample_airport()
        route2 = sample_route(destination=destination)

        serializer1 = RouteListSerializer(route1)
        serializer2 = RouteListSerializer(route2)

        res = self.client.get(ROUTE_URL, {"destination": destination.id})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer2.data, res.data["results"])
        self.assertNotIn(serializer1.data, res.data["results"])

        ...

    def test_retrieve_route_detail(self):
        route = sample_route()
        serializer = RouteRetrieveSerializer(route)

        res = self.client.get(
            reverse("airport:routes-detail", args=[route.id])
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_route_forbidden(self):
        source = sample_airport(
            name="TestSource", closest_big_city="TestSourceCity"
        )
        destination = sample_airport(
            name="TestDestination", closest_big_city="TestDestinationCity"
        )
        payload = {
            "source": source.name,
            "destination": destination.name,
            "distance": 100,
        }
        res = self.client.post(ROUTE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminUserRouteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test", password="TESTPASSWORD", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_route(self):
        source = sample_airport(
            name="TestSource", closest_big_city="TestSourceCity"
        )
        destination = sample_airport(
            name="TestDestination", closest_big_city="TestDestinationCity"
        )
        payload = {
            "source": source.name,
            "destination": destination.name,
            "distance": 100,
        }
        res = self.client.post(ROUTE_URL, payload)
        routes = Route.objects.all()
        route = Route.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(routes.count(), 1)
        self.assertEqual(route.source.name, payload["source"])
        self.assertEqual(route.destination.name, payload["destination"])
        self.assertEqual(route.distance, payload["distance"])

    def test_delete_route(self):
        route = sample_route()
        res = self.client.delete(
            reverse("airport:routes-detail", args=[route.id])
        )

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
