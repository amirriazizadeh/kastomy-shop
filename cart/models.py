from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
# from stores.models import StoreItem
# from products.models import Product


class Cart(models.Model):
    class Meta:
        verbose_name = "سبد خرید"
        verbose_name_plural = "سبدهای خرید"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='carts',
        verbose_name="کاربر"
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="قیمت کل"
    )
    total_discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="تخفیف کل"
    )
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.pk and not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=3)
        super().save(*args, **kwargs)

    def update_total(self):
        items = self.items.all()
        self.total_price = sum(item.total_price for item in items)
        self.total_discount = sum(item.total_discount for item in items)
        self.save(update_fields=['total_price', 'total_discount'])

    def get_final_price(self):
        return self.total_price - self.total_discount

    def __str__(self):
        return f"سبد خرید {self.user}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    store_item = models.ForeignKey('stores.StoreItem', on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)

    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    total_item_price = models.DecimalField(max_digits=12, decimal_places=2)
    total_discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['cart', 'store_item']
        indexes = [models.Index(fields=['cart', 'store_item'])]

    def __str__(self):
        return f"{self.store_item.product.name} x {self.quantity}"

    @property
    def product(self):
        return self.store_item.product.name

    @property
    def store(self):
        return self.store_item.store

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.quantity > self.store_item.stock:
            raise ValidationError(f"موجودی کافی نیست. موجودی فعلی: {self.store_item.stock}")

    def save(self, *args, **kwargs):
        base_price = self.store_item.price
        discount_price = (
            self.store_item.discount_price if self.store_item.discount_price else base_price
        )

        self.unit_price = discount_price
        self.total_item_price = base_price * self.quantity
        self.total_discount = (base_price - discount_price) * self.quantity
        self.total_price = discount_price * self.quantity

        super().save(*args, **kwargs)
        self.cart.update_total()
