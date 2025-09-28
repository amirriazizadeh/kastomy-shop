from django.utils import timezone
from django.db import models
from django.conf import settings
from core.models import BaseModel
from stores.models import StoreItem
from accounts.models import Address

class Order(models.Model):
    
    class OrderStatus(models.IntegerChoices):
        PENDING = 1, 'منتظر پرداخت'
        PAIED = 2, 'پرداخت شده'
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
    is_paid = models.BooleanField(default=False, verbose_name="پرداخت شده؟")

    tracking_code = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="کد رهگیری مرسوله"
    )

    description = models.TextField(
        null=True,
        blank=True,
        verbose_name="یادداشت مشتری"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    class Meta:
        verbose_name = "سفارش"
        verbose_name_plural = "سفارش‌ها"
        ordering = ['-created_at']

    payment_reference = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="کد پیگیری پرداخت (RefID)"
    )
    
    # فیلد جدید برای ذخیره کد Authority
    payment_authority = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="کد Authority زرین‌پال"
    )

    def __str__(self):
        return f"سفارش شماره {self.id} برای کاربر {self.user.phone_number}"
    

class OrderItem(models.Model):
    
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
        return f"{self.quantity} عدد از {self.store_item.variant.product.name} در سفارش {self.order.id}"

    @property
    def subtotal(self):
        return self.quantity * self.price


class Discount(models.Model):
    
    class Meta:
        verbose_name = "تخفیف"
        verbose_name_plural = "تخفیف‌ها"

    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    percent = models.PositiveIntegerField()
    expire_at = models.DateTimeField()
    usage_limit = models.PositiveIntegerField(default=1)  # تعداد مجاز استفاده هر کاربر

    def __str__(self):
        return self.code

class DiscountUsage(models.Model):
    
    class Meta:
        verbose_name = "استفاده از تخفیف"
        verbose_name_plural = "استفاده‌های تخفیف"

    discount = models.ForeignKey(Discount, on_delete=models.CASCADE, related_name='usages')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('discount', 'user')  # جلوگیری از ثبت چند ردیف تکراری


class Payment(models.Model):
    
    class PaymentStatus(models.IntegerChoices):
        PENDING = 1, 'در انتظار پرداخت'
        SUCCESSFUL = 2, 'موفق'
        FAILED = 3, 'ناموفق'

    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name='payments',
        verbose_name="سفارش"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="مبلغ")
    status = models.PositiveSmallIntegerField(
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        db_index=True,
        verbose_name="وضعیت پرداخت"
    )
    payment_gateway = models.CharField(max_length=50, blank=True, verbose_name="درگاه پرداخت")
    transaction_id = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="شناسه تراکنش",
        help_text="شناسه منحصر به فردی که از درگاه پرداخت دریافت می‌شود."
    )
    gateway_response = models.JSONField(
        null=True,
        blank=True,
        verbose_name="پاسخ درگاه",
        help_text="پاسخ کامل دریافت شده از درگاه برای دیباگ و پیگیری."
    )
    created_at = models.DateTimeField(auto_now_add=True,verbose_name='تاریخ پرداخت')
    class Meta:
        verbose_name = "پرداخت"
        verbose_name_plural = "پرداخت‌ها"
        ordering = ['-created_at']

    def __str__(self):
        return f"پرداخت برای سفارش {self.order.id} - وضعیت: {self.get_status_display()}"

