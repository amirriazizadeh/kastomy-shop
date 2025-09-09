from django.db import models
from core.models import BaseModel
from orders.models import Order

class Payment(BaseModel):
    """
    Stores a record for each payment attempt associated with an order.
    """
    class PaymentStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        SUCCESSFUL = 'SUCCESSFUL', 'Successful'
        FAILED = 'FAILED', 'Failed'
    
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    transaction_id = models.CharField(max_length=255, blank=True, help_text="From payment gateway")
    payment_gateway = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return f"Payment for Order {self.order.id} with status {self.status}"
