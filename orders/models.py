from django.db import models
from django.conf import settings
from core.models import BaseModel
from products.models import StoreItem
from users.models import Address

class Order(BaseModel):
    
    class OrderStatus(models.IntegerChoices):
        PENDING = 1, 'منتظر پرداخت'
        PROCESSING = 2, 'در حال پردازش'
        SHIPPED = 3, 'ارسال شده'
        DELIVERED = 4, 'تحویل شده'
        CANCELLED = 5, 'لغو شده'
        REFUNDED = 6, 'مرجوع شده'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name="کاربر"
    )
    shipping_address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        null=True,
        related_name='orders',
        verbose_name="آدرس ارسال"
    )
    total_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="مبلغ کل (بدون تخفیف)")
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="مبلغ تخفیف")
    final_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="مبلغ نهایی پرداخت")
    status = models.PositiveSmallIntegerField(
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
        verbose_name="وضعیت کلی سفارش"
    )

    class Meta:
        verbose_name = "سفارش"
        verbose_name_plural = "سفارش‌ها"
        ordering = ['-created_at']

    def __str__(self):
        return f"سفارش شماره {self.id} برای کاربر {self.user.phone_number}"

class OrderItem(BaseModel):
    
    class OrderItemStatus(models.IntegerChoices):
        PENDING = 1, 'در انتظار تایید'
        PREPARING = 2, 'در حال آماده‌سازی'
        SHIPPED = 3, 'ارسال شده'
        DELIVERED = 4, 'تحویل داده شده'
        CANCELLED = 5, 'لغو شده'
        RETURNED = 6, 'مرجوع شده'

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="سفارش")
    store_item = models.ForeignKey(
        StoreItem,
        on_delete=models.PROTECT,
        related_name='order_items',
        verbose_name="آیتم فروشگاه"
    )
    quantity = models.PositiveIntegerField(verbose_name="تعداد")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="قیمت در زمان خرید",
        
    )
    status = models.PositiveSmallIntegerField(
        choices=OrderItemStatus.choices,
        default=OrderItemStatus.PENDING,
        verbose_name="وضعیت آیتم"
    )

    class Meta:
        verbose_name = "آیتم سفارش"
        verbose_name_plural = "آیتم‌های سفارش"

    def __str__(self):
        return f"{self.quantity} عدد از {self.store_item.product.name} در سفارش {self.order.id}"

    @property
    def subtotal(self):
        return self.quantity * self.price
