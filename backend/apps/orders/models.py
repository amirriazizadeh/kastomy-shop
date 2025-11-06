from django.db import models
from apps.core.models import SoftDeleteModel, HardDeleteManager
from apps.addresses.models import Address
from apps.stores.models import StoreItem
from django.conf import settings


class Order(SoftDeleteModel):
    class OrderStatus(models.IntegerChoices):
        PENDING = 1, "PENDING"
        PROCESSING = 2, "PROCESSING"
        DELIVERED = 3, "DELIVERED"
        CANCELLED = 4, "CANCELLED"
        FAILED = 5, "FAILED"

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders"
    )
    address = models.ForeignKey(
        Address, on_delete=models.PROTECT, related_name="orders"
    )
    status = models.IntegerField(
        choices=OrderStatus.choices, default=OrderStatus.PENDING
    )
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def delete(self, *args, **kwargs):
        for item in self.items.all():  # type: ignore
            item.delete()
        super().delete(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.pk}. {self.customer} order with status {self.status} for address {self.address}"


class HardDeleteOrder(Order):
    objects = HardDeleteManager()

    class Meta:
        proxy = True
        verbose_name = "deleted order"
        verbose_name_plural = "deleted orders"


class OrderItem(SoftDeleteModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    store_item = models.ForeignKey(
        StoreItem, on_delete=models.PROTECT, related_name="order_items"
    )
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self) -> str:
        return f"{self.order.customer} order item in order {self.order}"


class HardDeleteOrderItem(OrderItem):
    objects = HardDeleteManager()

    class Meta:
        proxy = True
        verbose_name = "deleted Order item"
        verbose_name_plural = "deleted Order items"
