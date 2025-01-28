from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from airport.models import AirplaneType

# Create your tests here.
AIRPLANE_TYPE_URL = reverse('airport:airplane_types-list')


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
        self.user = get_user_model().create_user(
            {
                "email": "test@user.com",
                "password": "testpassword",
            }
        )
        self.client.force_authorize(self.user)
