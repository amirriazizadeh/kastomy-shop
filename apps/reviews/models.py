from django.db import models
from django.conf import settings
from apps.core.models import BaseModel
from apps.products.models import Product
from apps.stores.models import Store
from django.core.validators import MinValueValidator, MaxValueValidator


class Review(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_reviews"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="product_reviews",
        null=True,
        blank=True,
    )
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name="store_reviews",
        null=True,
        blank=True,
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True, null=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    (models.Q(product__isnull=False) & models.Q(store__isnull=True))
                    | (models.Q(product__isnull=True) & models.Q(store__isnull=False))
                ),
                name="exactly_one_review_target",
            )
        ]

    def __str__(self):
        if self.product:
            return f"Review by {self.user} for product {self.product.name}"
        else:
            return f"Review by {self.user} for store {self.store.name}"  # type: ignore
