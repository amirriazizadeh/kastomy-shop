from django.db import models
from django.conf import settings
from core.models import BaseModel


class Store(BaseModel):
    
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='store',
        verbose_name="مالک فروشگاه"
    )
    name = models.CharField(max_length=200, unique=True, verbose_name="نام فروشگاه")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    address = models.TextField(verbose_name="آدرس فروشگاه")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        verbose_name = "فروشگاه"
        verbose_name_plural = "فروشگاه‌ها"

    def __str__(self):
        return self.name