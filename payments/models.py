from django.db import models
from django.conf import settings
from core.models import BaseModel
from orders.models import Order

class Payment(BaseModel):
    
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

    class Meta:
        verbose_name = "پرداخت"
        verbose_name_plural = "پرداخت‌ها"
        ordering = ['-created_at']

    def __str__(self):
        return f"پرداخت برای سفارش {self.order.id} - وضعیت: {self.get_status_display()}"

