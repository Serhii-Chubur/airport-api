from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from airport.models import Route, Airport

# Create your tests here.
CREW_URL = reverse("airport:routes-list")


def sample_route(**params) -> Route:
    """Create and return a sample crew"""
    source_test_name, destination_test_name = (
        params.get("source_name", "TestSource"),
        params.get("destination_name", "TestDestination"),
    )
    source_test_city, destination_test_city = (
        params.get("source_city", "TestSourceCity"),
        params.get("destination_city", "TestDestinationCity"),
    )
    distance = params.get("distance", 100)
    source = Airport.objects.create(
        name=source_test_name, closest_big_city=source_test_city
    )
    destination = Airport.objects.create(
        name=destination_test_name, closest_big_city=destination_test_city
    )
    defaults = {
        "source": source,
        "destination": destination,
        "distance": distance,
    }
    defaults.update(params)
    return Route.objects.create(**defaults)


class UnauthorizedCrewApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_route_list(self):
        route = sample_route(source_name="1", destination_name="2")
        print(route)

    def test_auth_required(self):
        res = self.client.get(CREW_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


#
#
# class AuthorizedCrewApiTests(TestCase):
#     def setUp(self):
#         self.client = APIClient()
#         self.user = get_user_model().objects.create_user(
#             email="test@test.test",
#             password="TESTPASSWORD"
#         )
#         self.client.force_authenticate(self.user)
#
#     def test_crews_list(self):
#         sample_crew()
#         sample_crew(first_name="Test1", last_name="Test1")
#
#         crews = Crew.objects.all()
#
#         serializer = CrewListSerializer(crews, many=True)
#
#         res = self.client.get(CREW_URL)
#
#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         self.assertEqual(res.data["results"], serializer.data)
#
#     def test_retrieve_crew_detail(self):
#         crew = sample_crew()
#         serializer = CrewRetrieveSerializer(crew)
#
# res = self.client.get(reverse('airport:crews-detail', args=[crew.id]))
#
#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         self.assertEqual(res.data, serializer.data)
#
#     def test_create_crew_forbidden(self):
#         payload = {
#             "first_name": "Test2",
#             "last_name": "Test2",
#         }
#         res = self.client.post(CREW_URL, payload)
#
#         self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
#
#
# class AdminUserCrewApiTests(TestCase):
#     def setUp(self):
#         self.client = APIClient()
#         self.user = get_user_model().objects.create_user(
#             email="test@test.test",
#             password="TESTPASSWORD",
#             is_staff=True
#         )
#         self.client.force_authenticate(self.user)
#
#     def test_create_crew(self):
#         payload = {
#             "first_name": "Test3",
#             "last_name": "Test3",
#         }
#         res = self.client.post(CREW_URL, payload)
#         crews = Crew.objects.all()
#
#         self.assertEqual(res.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(crews.count(), 1)
#         self.assertEqual(crews[0].first_name, payload["first_name"])
#         self.assertEqual(crews[0].last_name, payload["last_name"])
#
#     def test_delete_crew(self):
#         crew = sample_crew()
#         res = self.client.delete(
#             reverse(
#                 'airport:crews-detail',
#                 args=[crew.id]
#             )
#         )
#
#         self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
