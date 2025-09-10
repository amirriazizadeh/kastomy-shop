from django.db import models
from core.models import BaseModel

class Category(BaseModel):
    
    name = models.CharField(max_length=200, verbose_name="نام دسته‌بندی")
    slug = models.SlugField(max_length=250, unique=True, allow_unicode=True, verbose_name="اسلاگ")
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
        verbose_name="دسته‌بندی والد"
    )
    is_sub = models.BooleanField(default=False)

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"

    def __str__(self):
        return self.name
