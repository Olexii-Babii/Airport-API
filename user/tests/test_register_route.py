from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


class UnauthenticatedUserRegisterTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_unauthenticated_can_register(self):
        data = {
            "email" : "testuser@gmail.com",
            "password" : "test1234"
        }
        response = self.client.post(reverse("user:create"), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_use_email_instead_username(self):
        data = {
            "username" : "testuser",
            "password" : "test1234"
        }
        response = self.client.post(reverse("user:create"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        