from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from apps.users.models import User
from apps.addresses.models import Address
from apps.stores.models import Store


class AddressAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(  # type: ignore
            email="user@example.com", password="password123", phone="09120000000"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.store = Store.objects.create(
            seller=self.user, name="Test Store", description="Store description"
        )
        self.address = Address.objects.create(
            user=self.user,
            store=self.store,
            label="Home",
            city="Tehran",
            state="Tehran",
            postal_code="12345",
            country="Iran",
        )

    def test_list_addresses(self):
        url = reverse("address_list_create")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # type: ignore
        self.assertEqual(response.data[0]["label"], "Home")  # type: ignore

    def test_create_address(self):
        url = reverse("address_list_create")
        data = {
            "store": self.store.id,  # type: ignore
            "label": "Work",
            "city": "Mashhad",
            "state": "Khorasan",
            "postal_code": "67890",
            "country": "Iran",
            "is_default": True,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Address.objects.count(), 2)
        self.assertEqual(response.data["label"], "Work")  # type: ignore

    def test_retrieve_address(self):
        url = reverse("address_detail_update_delete", kwargs={"pk": self.address.id})  # type: ignore
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["label"], "Home")  # type: ignore

    def test_update_address_put(self):
        url = reverse("address_detail_update_delete", kwargs={"pk": self.address.id})  # type: ignore
        data = {
            "store": self.store.id,  # type: ignore
            "label": "Updated",
            "city": "Esfahan",
            "state": "Esfahan",
            "postal_code": "11111",
            "country": "Iran",
            "is_default": False,
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.address.refresh_from_db()
        self.assertEqual(self.address.label, "Updated")
        self.assertEqual(self.address.city, "Esfahan")

    def test_partial_update_address_patch(self):
        url = reverse("address_detail_update_delete", kwargs={"pk": self.address.id})  # type: ignore
        data = {"city": "Qom"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.address.refresh_from_db()
        self.assertEqual(self.address.city, "Qom")

    def test_delete_address(self):
        url = reverse("address_detail_update_delete", kwargs={"pk": self.address.id})  # type: ignore
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Address.objects.filter(id=self.address.id).exists())  # type: ignore

    def test_retrieve_nonexistent_address(self):
        url = reverse("address_detail_update_delete", kwargs={"pk": 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["message"], "no such address")  # type: ignore

    def test_user_cannot_access_other_users_address(self):
        other_user = User.objects.create_user(
            email="other@example.com", password="password123", phone="09120000099"
        )  # type: ignore
        other_address = Address.objects.create(
            user=other_user,
            label="Other Home",
            city="Tabriz",
            state="East Azerbaijan",
            postal_code="44444",
            country="Iran",
        )
        url = reverse("address_detail_update_delete", kwargs={"pk": other_address.id})  # type: ignore
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = self.client.put(url, {"label": "Hacked!"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = self.client.patch(url, {"city": "HackedCity"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Address.objects.filter(id=other_address.id).exists())  # type: ignore
