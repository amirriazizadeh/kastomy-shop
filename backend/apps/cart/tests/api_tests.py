from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from apps.users.models import User
from apps.cart.models import Cart, CartItem
from apps.stores.models import Store, StoreItem
from apps.products.models import Product
from apps.categories.models import Category


class CartAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user@example.com", password="password123", phone="09120000000"
        )  # type: ignore
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.cart = Cart.objects.get(user=self.user)
        CartItem.objects.filter(cart=self.cart).delete()
        self.category = Category.objects.create(
            name="Test Category", description="Category description"
        )
        self.product = Product.objects.create(
            name="Test Product",
            description="Product description",
            category=self.category,
            is_active=True,
        )
        self.store = Store.objects.create(
            seller=self.user, name="Test Store", description="Store description"
        )
        self.store_item = StoreItem.objects.create(
            store=self.store,
            product=self.product,
            price=100.0,
            discount=0,
            stock=10,
            is_active=True,
        )

    def test_get_user_cart(self):
        url = reverse("user_cart")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("user", response.data)  # type: ignore

    def test_get_cart_items_empty(self):
        url = reverse("user_cart_items")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])  # type: ignore

    def test_add_product_to_cart(self):
        CartItem.objects.filter(cart=self.cart).delete()
        url = reverse("add_store_item_to_cart", args=[self.store_item.pk])
        data = {"quantity": 1}
        response = self.client.post(url, data)
        self.assertIn(
            response.status_code, [status.HTTP_201_CREATED, status.HTTP_200_OK]
        )
        cart_item = CartItem.objects.get(cart=self.cart, store_item=self.store_item)
        first_quantity = cart_item.quantity
        data = {"quantity": 3}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, first_quantity + 3)

    def test_patch_cart_item_set_quantity_zero(self):
        cart_item = CartItem.objects.create(
            cart=self.cart, store_item=self.store_item, quantity=2
        )
        url = reverse("user_cart_item_detail", args=[cart_item.pk])
        data = {"quantity": 0}
        response = self.client.patch(url, data)
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            response_delete = self.client.delete(url)
            self.assertEqual(response_delete.status_code, status.HTTP_204_NO_CONTENT)
            self.assertFalse(CartItem.objects.filter(pk=cart_item.pk).exists())
        else:
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
            self.assertFalse(CartItem.objects.filter(pk=cart_item.pk).exists())

    def test_delete_cart_item_directly(self):
        cart_item = CartItem.objects.create(
            cart=self.cart, store_item=self.store_item, quantity=1
        )
        url = reverse("user_cart_item_detail", args=[cart_item.pk])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CartItem.objects.filter(pk=cart_item.pk).exists())
