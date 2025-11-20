from django.urls import include, path
from rest_framework import routers

from airport import views

router = routers.DefaultRouter()
router.register("airports", views.AirportViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "airport"