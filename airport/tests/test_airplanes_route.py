import os.path
import tempfile

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import AirplaneType, Airplane
from airport.serializers import AirplaneListSerializer

AIRPLANE_URL = reverse("airport:airplane-list")

def sample_airplane_type(**params):
    default = {
        "name" : "test airplane type"
    }
    default.update(params)
    return AirplaneType.objects.create(**default)

def sample_airplane(airplane_type=None, **params):
    if not airplane_type:
        airplane_type = sample_airplane_type()

    default = {
        "name" : "test airplane",
        "rows" : 15,
        "seats_in_row" : 20,
        "airplane_type" : airplane_type
    }
    default.update(params)
    return Airplane.objects.create(**default)

def image_upload_url(airplane_id):
    """Return URL for recipe image upload"""
    return reverse("airport:airplane-upload-image", args=[airplane_id])

class UnauthenticatedUserAirplaneTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.airplane_type = sample_airplane_type(
            name="new test airplane type"
        )
        sample_airplane()

    def test_unauthenticated_airplane_list(self):
        response = self.client.get(AIRPLANE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_unauthenticated_create_airplane(self):
        data = {
            "name": "my airplane",
            "rows": 15,
            "seats_in_row": 20,
            "airplane_type": self.airplane_type.id
        }
        response = self.client.post(AIRPLANE_URL, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_retrieve_airplane(self):
        response = self.client.get(reverse("airport:airplane-detail", kwargs={"pk" : 1}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedUserAirplaneTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@gmail.com",
            password="test1234"
        )
        self.airplane_type = sample_airplane_type(
            name="new test airplane type"
        )
        sample_airplane()

        self.client.force_authenticate(self.user)

    def test_authenticated_airplane_list(self):
        sample_airplane(
            name="sample airplane 2",
            airplane_type=self.airplane_type
        )

        sample_airplane(
            name="sample airplane 3",
            airplane_type=self.airplane_type
        )
        response = self.client.get(AIRPLANE_URL)
        serializer = AirplaneListSerializer(Airplane.objects.all(), many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_authenticated_create_airplane(self):
        data = {
            "name": "my airplane",
            "rows": 15,
            "seats_in_row": 20,
            "airplane_type": self.airplane_type.id
        }
        response = self.client.post(AIRPLANE_URL, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_retrieve_airplane(self):
        response = self.client.get(reverse("airport:airplane-detail", kwargs={"pk" : 1}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AdminUserAirplaneTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            email="test@gmail.com",
            password="test1234"
        )
        self.airplane_type = sample_airplane_type(
            name="new test airplane type"
        )
        sample_airplane()

        self.client.force_authenticate(self.user)

    def test_admin_airplane_list(self):
        sample_airplane(
            name="sample airplane 1",
            airplane_type=sample_airplane_type(
                name="test airplane type 1"
            )
        )

        sample_airplane(
            name="sample airplane 2",
            airplane_type=sample_airplane_type(
                name="test airplane type 2"
            )
        )
        response = self.client.get(AIRPLANE_URL)
        serializer = AirplaneListSerializer(Airplane.objects.all(), many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_admin_create_airplane(self):
        data = {
            "name": "my airplane",
            "rows": 15,
            "seats_in_row": 20,
            "airplane_type": self.airplane_type.id
        }
        response = self.client.post(AIRPLANE_URL, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admin_retrieve_airplane(self):
        sample_airplane(
            name="sample airplane 1",
            airplane_type=sample_airplane_type(
                name="test airplane type 1"
            )
        )

        sample_airplane(
            name="sample airplane 2",
            airplane_type=sample_airplane_type(
                name="test airplane type 2"
            )
        )
        response = self.client.get(reverse("airport:airplane-detail", kwargs={"pk" : 1}))
        serializer = AirplaneListSerializer(Airplane.objects.get(pk=1), many=False)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)


class AirplaneImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            email="test@gmail.com",
            password="test1234"
        )
        self.airplane = sample_airplane()
        self.airplane_type = sample_airplane_type(
            name="airplane image type"
        )
        self.client.force_authenticate(self.user)

    def tearDown(self):
        self.airplane.image.delete()

    def test_upload_image_to_airplane(self):
        url = image_upload_url(self.airplane.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            response = self.client.post(url, {"image" : ntf}, format="multipart")
        self.airplane.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("image", response.data)
        self.assertTrue(os.path.exists(self.airplane.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.airplane.id)
        response = self.client.post(url, {"image" : "not image"}, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_image_to_airport_list(self):
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            response = self.client.post(
                AIRPLANE_URL,
                {
                    "name" : "new airplane",
                    "rows" : 10,
                    "seats_in_row" : 10,
                    "airplane_type" : self.airplane_type.id,
                    "image" : ntf
                },
                format="multipart"
            )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        airplane = Airplane.objects.get(name="new airplane")
        self.assertFalse(airplane.image)

    def test_image_url_is_shown_on_airport_detail(self):
        url = image_upload_url(self.airplane.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")

        response = self.client.get(AIRPLANE_URL + f"{self.airplane.id}/")
        self.assertIn("image", response.data)

    def test_image_url_is_shown_on_airport_list(self):
        url = image_upload_url(self.airplane.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")

        response = self.client.get(AIRPLANE_URL)
        self.assertIn("image", response.data["results"][0].keys())
