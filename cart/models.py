from decimal import Decimal
from django.db import models
from django.conf import settings
from core.models import BaseModel
from stores.models import StoreItem


class Cart(BaseModel):
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='carts',
        verbose_name="کاربر"
    )
    
    total_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'), 
        verbose_name="قیمت کل"
    )
    is_active = models.BooleanField(default=True,verbose_name="فعال")

    class Meta:
        verbose_name = "سبد خرید"
        verbose_name_plural = "سبدهای خرید"

    def __str__(self):
        if self.user:
            return f"سبد خرید کاربر {self.user.phone_number}"
        return f"سبد خرید مهمان - {self.session_key}"

class CartItem(BaseModel):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="سبد خرید"
    )
    store_item = models.ForeignKey(
        StoreItem,
        on_delete=models.CASCADE,
        related_name='cart_items',
        verbose_name="آیتم فروشگاه"
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="تعداد")
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="قیمت واحد در زمان افزودن"
    )

    class Meta:
        verbose_name = "آیتم سبد خرید"
        verbose_name_plural = "آیتم‌های سبد خرید"

    def __str__(self):
        return f"{self.quantity} عدد از {self.store_item.variant.product.name}"

    @property
    def total_price(self):
        return self.quantity * self.price
