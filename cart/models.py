from django.db import models
from django.conf import settings
from core.models import BaseModel
from products.models import StoreItem

class Cart(BaseModel):
    """
    Represents a shopping cart, for a registered user or a guest.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='carts')
    session_key = models.CharField(max_length=40, null=True, blank=True, help_text="For guest users")

    def __str__(self):
        if self.user:
            return f"Cart for {self.user.phone_number}"
        return f"Guest Cart - {self.session_key}"

class CartItem(BaseModel):
    """
    Represents an item within a shopping cart.
    It now links to a StoreItem, not a ProductVariant.
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(StoreItem, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'item')

    def __str__(self):
        return f"{self.quantity} x {self.item.variant.product.name}"

    @property
    def total_price(self):
        return self.quantity * self.item.price
