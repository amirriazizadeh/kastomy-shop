from django.test import TestCase
from apps.users.models import User
from apps.stores.models import Store
from apps.addresses.models import Address


class AddressModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(  # type: ignore
            email="test@example.com", password="TestPass123", phone="09120000000"
        )
        self.store = Store.objects.create(
            seller=self.user, name="Test Store", description="Test Store Description"
        )

    def test_create_address_without_store(self):
        address = Address.objects.create(
            user=self.user,
            label="Home",
            city="Tehran",
            state="Tehran",
            postal_code="12345",
            country="Iran",
            is_default=True,
        )
        self.assertEqual(str(address), f"{self.user} address")
        self.assertEqual(address.city, "Tehran")
        self.assertTrue(address.is_default)
        self.assertIsNone(address.store)

    def test_create_address_with_store(self):
        address = Address.objects.create(
            user=self.user,
            store=self.store,
            label="Work",
            city="Mashhad",
            state="Khorasan",
            postal_code="67890",
            country="Iran",
        )
        self.assertEqual(address.store, self.store)
        self.assertEqual(address.label, "Work")
        self.assertFalse(address.is_default)

    def test_update_address(self):
        address = Address.objects.create(
            user=self.user,
            label="Temp",
            city="Shiraz",
            state="Fars",
            postal_code="22222",
            country="Iran",
        )
        address.city = "Esfahan"
        address.is_default = True
        address.save()

        updated = Address.objects.get(id=address.id)  # type: ignore
        self.assertEqual(updated.city, "Esfahan")
        self.assertTrue(updated.is_default)

    def test_delete_address(self):
        address = Address.objects.create(
            user=self.user,
            label="ToDelete",
            city="Qom",
            state="Qom",
            postal_code="33333",
            country="Iran",
        )
        address_id = address.id  # type: ignore
        address.delete()
        self.assertFalse(Address.objects.filter(id=address_id).exists())
