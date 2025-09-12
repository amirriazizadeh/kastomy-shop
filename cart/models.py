from django.db import models
from django.conf import settings
from core.models import BaseModel
from products.models import StoreItem

class Cart(BaseModel):
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='carts',
        verbose_name="کاربر"
    )
    session_key = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        db_index=True,
        verbose_name="شناسه جلسه (برای کاربر مهمان)"
    )

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

    class Meta:
        verbose_name = "آیتم سبد خرید"
        verbose_name_plural = "آیتم‌های سبد خرید"
       

    def __str__(self):
        return f"{self.quantity} عدد از {self.store_item.product.name}"

    @property
    def total_price(self):
        return self.quantity * self.store_item.price

