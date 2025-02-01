import os
import tempfile

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from airport.models import Airplane
from airport.serializers import (
    AirplaneListSerializer,
    AirplaneRetrieveSerializer,
)
from airport.tests.test_airplane_type_api import sample_airplane_type

# Create your tests here.
AIRPLANE_URL = reverse("airport:airplanes-list")


def sample_airplane(**params) -> Airplane:
    """Create and return a sample airplane"""
    airplane_type = sample_airplane_type()
    defaults = {
        "name": "TestName",
        "rows": 10,
        "seats_in_row": 4,
        "airplane_type": airplane_type,
        "image": None,
    }
    defaults.update(params)
    return Airplane.objects.create(**defaults)


def image_upload_url(airplane_id):
    return reverse("airport:airplanes-upload-image", args=[airplane_id])


def detail_url(airplane_id):
    return reverse("airport:airplanes-detail", args=[airplane_id])


class UnauthorizedAirplaneApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(AIRPLANE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedAirplaneApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test", password="TESTPASSWORD"
        )
        self.client.force_authenticate(self.user)

    def test_airplane_list(self):
        sample_airplane()
        sample_airplane(name="Airplane")

        airplanes = Airplane.objects.all()
        res = self.client.get(AIRPLANE_URL)
        serializer = AirplaneListSerializer(airplanes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_airplane_list_filter_by_airplane_type(self):
        airplane1 = sample_airplane()
        airplane_type = sample_airplane_type(name="Type2")
        airplane2 = sample_airplane(airplane_type=airplane_type)

        serializer1 = AirplaneListSerializer(airplane1)
        serializer2 = AirplaneListSerializer(airplane2)
        res = self.client.get(AIRPLANE_URL, {"type": airplane_type.id})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer2.data, res.data["results"])
        self.assertNotIn(serializer1.data, res.data["results"])

    def test_retrieve_airplane_detail(self):
        airplane = sample_airplane()
        serializer = AirplaneRetrieveSerializer(airplane)

        res = self.client.get(
            reverse("airport:airplanes-detail", args=[airplane.id])
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_airplane_forbidden(self):
        airplane_type = sample_airplane_type()
        payload = {
            "name": "TestName",
            "rows": 10,
            "seats_in_row": 4,
            "airplane_type": airplane_type.id,
        }
        res = self.client.post(AIRPLANE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminUserAirplaneApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test", password="TESTPASSWORD", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_airplane(self):
        airplane_type = sample_airplane_type()
        payload = {
            "id": 1,
            "name": "TestName",
            "rows": 10,
            "seats_in_row": 4,
            "airplane_type": airplane_type.id,
        }
        res = self.client.post(AIRPLANE_URL, payload)

        airplanes = Airplane.objects.all()
        airplane = Airplane.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(airplanes.count(), 1)
        self.assertEqual(airplane.name, payload["name"])
        self.assertEqual(airplane.rows, payload["rows"])
        self.assertEqual(airplane.seats_in_row, payload["seats_in_row"])
        self.assertEqual(airplane.airplane_type.id, payload["airplane_type"])

    def test_delete_airplane(self):
        airplane = sample_airplane()
        res = self.client.delete(
            reverse("airport:airplanes-detail", args=[airplane.id])
        )

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)


class AirplaneImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "admin@myproject.com", "password"
        )
        self.client.force_authenticate(self.user)
        self.airplane = sample_airplane()

    def tearDown(self):
        self.airplane.image.delete()

    def test_upload_image_to_airplane(self):
        """Test uploading an image to airplane"""
        url = image_upload_url(self.airplane.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")
        self.airplane.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.airplane.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.airplane.id)
        res = self.client.post(url, {"image": "not image"}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_image_to_airplane_list_should_not_work(self):
        url = AIRPLANE_URL
        airplane_type = sample_airplane_type()
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(
                url,
                {
                    "name": "Name",
                    "rows": 10,
                    "seats_in_row": 4,
                    "airplane_type": airplane_type.id,
                    "image": ntf,
                },
                format="multipart",
            )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        airplane = Airplane.objects.get(name="Name")
        self.assertFalse(airplane.image)

    def test_image_url_is_shown_on_airplane_detail(self):
        url = image_upload_url(self.airplane.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(detail_url(self.airplane.id))

        self.assertIn("image", res.data)
