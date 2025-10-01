from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from stores.models import StoreItem

class Cart(models.Model):
    class Meta:
        verbose_name = "سبد خرید"
        verbose_name_plural = "سبدهای خرید"
        permissions = [
            ("can_checkout_cart", "Can checkout cart"),     # اجازه نهایی‌کردن سبد خرید
            ("can_clear_cart", "Can clear cart"),           # اجازه خالی کردن کل سبد
            ("can_extend_cart", "Can extend cart expiry"),  # اجازه تمدید تاریخ انقضا
        ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='carts',
        verbose_name="کاربر"
    )
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="قیمت کل"
    )
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # تنظیم تاریخ انقضا هنگام ساخت
        if not self.pk and not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=3)
        super().save(*args, **kwargs)

    def update_total(self):
        self.total_price = sum(item.total_price for item in self.items.all())
        self.save(update_fields=['total_price'])

    def __str__(self):
        return f"سبد خرید {self.user}"

class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE,
        related_name='items',
        verbose_name="سبد خرید")
    store_item = models.ForeignKey(
        StoreItem, on_delete=models.CASCADE,
        related_name='cart_items', verbose_name="آیتم فروشگاه"
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="تعداد")
    price = models.DecimalField(
        max_digits=12, decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="قیمت واحد در زمان افزودن"
    )

    class Meta:
        verbose_name = "آیتم سبد خرید"
        verbose_name_plural = "آیتم‌های سبد خرید"
        permissions = [
            ("can_view_own_cartitems", "Can view own cart items"),         # دیدن آیتم‌های سبد خودش
            ("can_change_own_cartitems", "Can change own cart items"),     # تغییر آیتم‌های سبد خودش
            ("can_delete_own_cartitems", "Can delete own cart items"),     # حذف آیتم‌های سبد خودش
            ("can_apply_discount_item", "Can apply discount to cart item") # اجازه اعمال تخفیف روی آیتم
        ]
    

    def __str__(self):
        return f"{self.quantity} عدد از {self.store_item.variant.product.name}"

    @property
    def total_price(self):
        return self.quantity * self.price
