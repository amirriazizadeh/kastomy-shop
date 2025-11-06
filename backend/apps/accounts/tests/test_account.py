from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.core.cache import cache
from apps.users.models import User
from rest_framework_simplejwt.tokens import RefreshToken


class TestRequestOtp(APITestCase):
    def setUp(self):
        self.url = reverse("request_otp")
        self.email = "test@example.com"

    def test_request_otp_success(self):
        response = self.client.post(self.url, {"email": self.email})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)

    def test_request_otp_invalid_email(self):
        response = self.client.post(self.url, {"email": "not-an-email"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestVerifyOtp(APITestCase):
    def setUp(self):
        self.url = reverse("verify_otp")
        self.email = "verify@example.com"
        self.otp = 1234
        cache.set(f"otp_{self.email}", self.otp, timeout=60)
        self.user = User.objects.create_user(  # type: ignore
            email=self.email, password="TestPass123", phone="09120000000"
        )

    def test_verify_otp_success(self):
        response = self.client.post(self.url, {"email": self.email, "otp": self.otp})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)  # type: ignore
        self.assertIn("refresh", response.data)  # type: ignore

    def test_verify_otp_wrong_code(self):
        response = self.client.post(self.url, {"email": self.email, "otp": 9999})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_verify_otp_expired(self):
        cache.delete(f"otp_{self.email}")
        response = self.client.post(self.url, {"email": self.email, "otp": self.otp})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_verify_otp_user_not_found(self):
        User.objects.filter(email=self.email).delete()
        response = self.client.post(self.url, {"email": self.email, "otp": self.otp})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TestRegister(APITestCase):
    def setUp(self):
        self.url = reverse("register")

    def test_register_success(self):
        data = {
            "email": "newuser@example.com",
            "password": "TestPass123",
            "phone": "09120000001",
            "first_name": "Nima",
        }
        response = self.client.post(self.url, data)
        print("REGISTER RESPONSE:", response.data)  # type: ignore
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["email"], data["email"])  # type: ignore

    def test_register_invalid(self):
        response = self.client.post(self.url, {"email": "not-valid"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestLogout(APITestCase):
    def setUp(self):
        self.url = reverse("logout")
        self.user = User.objects.create_user(
            email="logout@example.com", password="TestPass123", phone="09120000002"
        ) # type: ignore
        self.token = RefreshToken.for_user(self.user)

    def test_logout_success(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token.access_token}") # type: ignore
        response = self.client.post(self.url, {"refresh": str(self.token)})
        self.assertIn(
            response.status_code, [status.HTTP_200_OK, status.HTTP_205_RESET_CONTENT]
        )

    def test_logout_invalid_token(self):
        response = self.client.post(self.url, {"refresh": "bad-token"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
