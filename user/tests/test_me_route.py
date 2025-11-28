from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


class UnauthenticatedUserMeTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@gmail.com",
            password="test1234"
        )

    def test_unauthenticated_get_me(self):
        response = self.client.get(reverse("user:me"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_put_me(self):
        data = {
            "email": "newemail@gmail.com",
            "password": "newpassword1234"
        }
        response = self.client.put(reverse("user:me"), data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedUserMeTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@gmail.com",
            password="test1234"
        )
        self.client.force_authenticate(self.user)

    def test_authenticated_get_me(self):
        response = self.client.get(reverse("user:me"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authenticated_put_me(self):
        data = {
            "email": "newemail@gmail.com",
            "password": "newpassword1234"
        }
        response = self.client.put(reverse("user:me"), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)