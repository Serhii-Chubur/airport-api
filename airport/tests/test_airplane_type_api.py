from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from airport.models import AirplaneType
from airport.serializers import (
    AirplaneTypeSerializer,
    AirplaneTypeRetrieveSerializer,
)

# Create your tests here.
AIRPLANE_TYPE_URL = reverse("airport:airplane_types-list")


def sample_airplane_type(**params) -> AirplaneType:
    """Create and return a sample airplane type"""
    defaults = {
        "name": "TestType",
    }
    defaults.update(params)
    return AirplaneType.objects.create(**defaults)


class UnauthorizedAirplaneTypeApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(AIRPLANE_TYPE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedAirplaneTypeApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test", password="TESTPASSWORD"
        )
        self.client.force_authenticate(self.user)

    def test_airplane_types_list(self):
        sample_airplane_type()
        sample_airplane_type(name="Test1")

        types = AirplaneType.objects.all()

        serializer = AirplaneTypeSerializer(types, many=True)

        res = self.client.get(AIRPLANE_TYPE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_retrieve_airplane_type_detail(self):
        airplane_type = sample_airplane_type()
        serializer = AirplaneTypeRetrieveSerializer(airplane_type)

        res = self.client.get(
            reverse("airport:airplane_types-detail", args=[airplane_type.id])
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_airplane_type_forbidden(self):
        payload = {
            "name": "TestType",
        }
        res = self.client.post(AIRPLANE_TYPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminUserAirplaneTypeApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test", password="TESTPASSWORD", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_airplane_type(self):
        payload = {
            "name": "TestType",
        }
        res = self.client.post(AIRPLANE_TYPE_URL, payload)
        types = AirplaneType.objects.all()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(types.count(), 1)
        self.assertEqual(types[0].name, payload["name"])

    def test_delete_airplane_type_forbidden(self):
        airplane_type = sample_airplane_type()
        res = self.client.delete(
            reverse("airport:airplane_types-detail", args=[airplane_type.id])
        )

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
