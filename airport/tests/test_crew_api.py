from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from airport.models import Crew
from airport.serializers import CrewRetrieveSerializer, CrewListSerializer

# Create your tests here.
CREW_URL = reverse("airport:crews-list")


def sample_crew(**params) -> Crew:
    """Create and return a sample crew"""
    defaults = {
        "first_name": "Test",
        "last_name": "Test",
    }
    defaults.update(params)
    return Crew.objects.create(**defaults)


class UnauthorizedCrewApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(CREW_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedCrewApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test", password="TESTPASSWORD"
        )
        self.client.force_authenticate(self.user)

    def test_crews_list(self):
        sample_crew()
        sample_crew(first_name="Test1", last_name="Test1")

        crews = Crew.objects.all()

        serializer = CrewListSerializer(crews, many=True)

        res = self.client.get(CREW_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_retrieve_crew_detail(self):
        crew = sample_crew()
        serializer = CrewRetrieveSerializer(crew)

        res = self.client.get(reverse("airport:crews-detail", args=[crew.id]))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_crew_forbidden(self):
        payload = {
            "first_name": "Test2",
            "last_name": "Test2",
        }
        res = self.client.post(CREW_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminUserCrewApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test", password="TESTPASSWORD", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_crew(self):
        payload = {
            "first_name": "Test3",
            "last_name": "Test3",
        }
        res = self.client.post(CREW_URL, payload)
        crews = Crew.objects.all()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(crews.count(), 1)
        self.assertEqual(crews[0].first_name, payload["first_name"])
        self.assertEqual(crews[0].last_name, payload["last_name"])

    def test_delete_crew(self):
        crew = sample_crew()
        res = self.client.delete(
            reverse("airport:crews-detail", args=[crew.id])
        )

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
