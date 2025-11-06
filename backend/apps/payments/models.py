from django.db import models
from apps.core.models import SoftDeleteModel, HardDeleteManager
from apps.orders.models import Order


class Payment(SoftDeleteModel):
    class PaymentStatus(models.IntegerChoices):
        PROGRESS = 1, "Progress"
        VERIFY = 2, "Verify"
        DONE = 3, "Done"
        FAILED = 4, "Failed"

    order = models.OneToOneField(
        Order, on_delete=models.PROTECT, related_name="payment"
    )
    status = models.IntegerField(
        choices=PaymentStatus.choices, default=PaymentStatus.PROGRESS
    )
    transaction_id = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    gateway = models.CharField(max_length=50, default="Zarin_Pal")

    def __str__(self) -> str:
        return f"{self.pk}. payment for order {self.order}"


class HardDeletePayment(Payment):
    objects = HardDeleteManager()

    class Meta:
        proxy = True
        verbose_name = "deleted Payment"
        verbose_name_plural = "deleted Payments"
