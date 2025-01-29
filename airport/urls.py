from django.urls import include, path
from rest_framework import routers

from airport import views

router = routers.DefaultRouter()
router.register(r"orders", views.OrderViewSet, basename="orders")
router.register(
    r"airplane-types", views.AirplaneTypeViewSet, basename="airplane_types"
)
router.register(r"crews", views.CrewViewSet, basename="crews")
router.register(r"airports", views.AirportViewSet, basename="airports")
router.register(r"routes", views.RouteViewSet, basename="routes")
router.register(r"airplanes", views.AirplaneViewSet, basename="airplanes")
router.register(r"flights", views.FlightViewSet, basename="flights")

urlpatterns = [path("", include(router.urls))]

app_name = "airport"
