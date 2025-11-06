from django.db import models
from apps.core.models import BaseModel, SoftDeleteModel, HardDeleteManager
from apps.categories.models import Category
from django.db.models.functions import Coalesce
from django.db.models import F, ExpressionWrapper, Value, DecimalField
from django.db.models import Sum


class Product(SoftDeleteModel):
    name = models.CharField(max_length=255)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products"
    )
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)  # type: ignore
    stock = models.PositiveIntegerField(default=20)

    @property
    def total_stock(self):
        aggregated_stock = self.store_items.filter(is_active=True).aggregate(  # type: ignore
            total=Coalesce(Sum("stock"), 0)  # type: ignore
        )["total"]
        return aggregated_stock or 0

    @property
    def best_price_item(self):
        item = (
            self.store_items.filter(is_active=True, stock__gt=0)  # type: ignore
            .annotate(
                current_price=ExpressionWrapper(
                    F("price") * (1 - Coalesce(F("discount"), Value(0)) / Value(100)),
                    output_field=DecimalField(max_digits=10, decimal_places=2),
                )
            )
            .order_by("current_price")
            .first()
        )
        return item

    @property
    def best_price(self):
        item = self.best_price_item
        if item:
            return item.current_price
        return None

    def __str__(self) -> str:
        return f"{self.name}"


class HardDeleteProduct(Product):
    objects = HardDeleteManager()

    class Meta:
        proxy = True
        verbose_name = "deleted product"
        verbose_name_plural = "deleted products"


class ProductImage(BaseModel):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="products/")

    def __str__(self) -> str:
        return f"{self.product} image"
