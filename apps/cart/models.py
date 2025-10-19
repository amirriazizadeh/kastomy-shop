from django.db import models
from apps.core.models import BaseModel
from django.conf import settings
from apps.stores.models import StoreItem
from django.core.exceptions import ValidationError


class Cart(BaseModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart"
    )

    def __str__(self) -> str:
        return f"{self.user} Cart"


class CartItem(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    store_item = models.ForeignKey(
        StoreItem, on_delete=models.CASCADE, related_name="storeItem_cartItem"
    )
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.store_item.product} cart item for user {self.cart.user.email}"

    class Meta:
        unique_together = ("cart", "store_item")

    def save(self, *args, **kwargs):
        if self.quantity < 0:
            raise ValidationError("Quantity must be a positive number.")
        if self.store_item.stock < self.quantity:
            raise ValidationError(
                f"Not enough stock for {self.store_item.product.name}. Available: {self.store_item.stock}"
            )
        super().save(*args, **kwargs)
