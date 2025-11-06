from django.db import models
from apps.core.models import BaseModel
from django.core.exceptions import ValidationError


class Category(BaseModel):
    name = models.CharField(max_length=255)
    image = models.ImageField(
        upload_to="categories/",
        null=True,
        blank=True,
    )
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        return self.name

    def clean(self):
        if self.parent and self.parent.id == self.id:  # type: ignore
            raise ValidationError("A category cannot be its own parent.")
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
