from django.db import models
from apps.core.models import BaseModel
from apps.users.models import User
from apps.stores.models import Store


class Address(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name="store_address",
        null=True,
        blank=True,
    )
    label = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_default = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.user} address"
