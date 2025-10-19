
from django.db import models
# from products.models import Product
from django.conf import settings
from apps.accounts.models import Address

class Store(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="stores")
    address = models.ForeignKey(Address,on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class StoreItem(models.Model):
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name="store_items")
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="items")
    price = models.DecimalField(max_digits=12, decimal_places=2)
    discount_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} - {self.store.name}"
