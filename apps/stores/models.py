from django.db import models
from apps.core.models import SoftDeleteModel, HardDeleteManager
from apps.products.models import Product
from django.conf import settings
from decimal import Decimal


class Store(SoftDeleteModel):
    name = models.CharField(max_length=255)
    description = models.TextField()
    seller = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="store"
    )

    def __str__(self) -> str:
        return f"{self.name} store for user {self.seller}"


class HardDeleteStore(Store):
    objects = HardDeleteManager()

    class Meta:
        proxy = True
        verbose_name = "deleted Store"
        verbose_name_plural = "deleted Stores"


class StoreItem(SoftDeleteModel):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="store_items"
    )
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="items")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Discount percentage, e.g., 20 for 20%",
    )
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.product} store item in {self.store}"

    @property
    def total_price(self):
        if self.discount:
            return self.price * (Decimal("1") - self.discount / Decimal("100"))
        return self.price

    def delete(self, using=None, keep_parents=False):
        self.storeItem_cartItem.all().delete()  # type: ignore
        super().delete(using=using, keep_parents=keep_parents)


class HardDeleteStoreItem(StoreItem):
    objects = HardDeleteManager()

    class Meta:
        proxy = True
        verbose_name = "deleted Store item"
        verbose_name_plural = "deleted Store items"
