from django.test import TestCase
from apps.cart.models import Cart, CartItem
from apps.users.models import User
from apps.stores.models import Store, StoreItem
from apps.products.models import Product
from apps.categories.models import Category


class CartModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user@example.com", password="password123", phone="09120000000"
        )  # type: ignore

        self.category = Category.objects.create(
            name="Test Category", description="Category description"
        )

        self.product = Product.objects.create(
            name="Test Product",
            description="Product description",
            category=self.category,
        )

        self.store = Store.objects.create(
            seller=self.user, name="Test Store", description="Store description"
        )

        self.store_item = StoreItem.objects.create(
            store=self.store,
            product=self.product,
            price=100.0,
            discount=10,
            stock=10,
            is_active=True,
        )

        self.cart, _ = Cart.objects.get_or_create(user=self.user)

    def test_cart_creation(self):
        self.assertEqual(self.cart.user, self.user)
        self.assertEqual(str(self.cart), f"{self.user} Cart")

    def test_add_cart_item(self):
        cart_item = CartItem.objects.create(
            cart=self.cart, store_item=self.store_item, quantity=2
        )
        self.assertEqual(cart_item.cart, self.cart)
        self.assertEqual(cart_item.store_item, self.store_item)
        self.assertEqual(cart_item.quantity, 2)

    def test_update_cart_item_quantity(self):
        cart_item = CartItem.objects.create(
            cart=self.cart, store_item=self.store_item, quantity=1
        )
        cart_item.quantity = 5
        cart_item.save()
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 5)

    def test_delete_cart_item(self):
        cart_item = CartItem.objects.create(
            cart=self.cart, store_item=self.store_item, quantity=1
        )
        cart_item_id = cart_item.id  # type: ignore
        cart_item.delete()
        self.assertFalse(CartItem.objects.filter(id=cart_item_id).exists())

    def test_unique_together_cartitem(self):
        CartItem.objects.create(cart=self.cart, store_item=self.store_item, quantity=1)
        with self.assertRaises(Exception):
            CartItem.objects.create(
                cart=self.cart, store_item=self.store_item, quantity=1
            )

    def test_delete_cart_cascade_cartitems(self):
        cart_item = CartItem.objects.create(
            cart=self.cart, store_item=self.store_item, quantity=1
        )
        self.cart.delete()
        self.assertFalse(CartItem.objects.filter(id=cart_item.id).exists())  # type: ignore

    def test_cannot_add_item_when_stock_zero(self):
        self.store_item.stock = 0
        self.store_item.save()
        with self.assertRaises(Exception):
            CartItem.objects.create(
                cart=self.cart, store_item=self.store_item, quantity=1
            )

    def test_cart_item_str(self):
        cart_item = CartItem.objects.create(
            cart=self.cart, store_item=self.store_item, quantity=1
        )
        self.assertIn(str(self.store_item.product), str(cart_item))
        self.assertIn(self.user.email, str(cart_item))

    def test_user_has_only_one_cart(self):
        with self.assertRaises(Exception):
            Cart.objects.create(user=self.user)

    def test_delete_store_item_cascade_cartitem(self):
        cart_item = CartItem.objects.create(
            cart=self.cart, store_item=self.store_item, quantity=1
        )
        cart_item_id = cart_item.id  # type: ignore
        self.store_item.delete()
        self.assertFalse(CartItem.objects.filter(id=cart_item_id).exists())
