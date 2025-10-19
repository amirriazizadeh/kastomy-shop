from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
from ..models import Cart, CartItem, StoreItem

User = get_user_model()


class CartModelTest(TestCase):
    """تست‌های مربوط به مدل Cart"""
    
    def setUp(self):
        """ایجاد داده‌های اولیه برای تست‌ها"""
        self.user = User.objects.create_user(
            phone_number='testuser',
            email='testuser@example.com',
            password='testpass123'
        )
        
    def test_cart_creation(self):
        """تست ایجاد سبد خرید"""
        cart = Cart.objects.create(user=self.user)
        
        self.assertEqual(cart.user, self.user)
        self.assertEqual(cart.total_price, Decimal('0.00'))
        self.assertTrue(cart.is_active)
        self.assertIsNotNone(cart.created_at)
        
    def test_cart_expires_at_auto_set(self):
        """تست تنظیم خودکار تاریخ انقضا"""
        cart = Cart.objects.create(user=self.user)
        
        # بررسی اینکه expires_at 3 روز بعد از الان است
        expected_expiry = timezone.now() + timedelta(days=3)
        time_diff = abs((cart.expires_at - expected_expiry).total_seconds())
        
        # اختلاف باید کمتر از 1 ثانیه باشد
        self.assertLess(time_diff, 1)
        
    def test_cart_custom_expires_at(self):
        """تست تنظیم دستی تاریخ انقضا"""
        custom_expiry = timezone.now() + timedelta(days=7)
        cart = Cart.objects.create(
            user=self.user,
            expires_at=custom_expiry
        )
        
        # زمان سفارشی باید حفظ شود
        time_diff = abs((cart.expires_at - custom_expiry).total_seconds())
        self.assertLess(time_diff, 1)
        
    def test_cart_str_representation(self):
        """تست نمایش رشته‌ای سبد خرید"""
        cart = Cart.objects.create(user=self.user)
        expected_str = f"سبد خرید {self.user}"
        
        self.assertEqual(str(cart), expected_str)
        
    def test_cart_user_relation(self):
        """تست رابطه بین کاربر و سبد خرید"""
        cart1 = Cart.objects.create(user=self.user)
        cart2 = Cart.objects.create(user=self.user)
        
        user_carts = self.user.carts.all()
        
        self.assertEqual(user_carts.count(), 2)
        self.assertIn(cart1, user_carts)
        self.assertIn(cart2, user_carts)
        
    def test_cart_delete_on_user_delete(self):
        """تست حذف سبد خرید با حذف کاربر"""
        cart = Cart.objects.create(user=self.user)
        cart_id = cart.id
        
        self.user.delete()
        
        self.assertFalse(Cart.objects.filter(id=cart_id).exists())




