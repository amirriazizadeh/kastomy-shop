from django.db import models
from django.conf import settings
from core.models import BaseModel

class Profile(BaseModel):
    
    class SellerRequestStatus(models.IntegerChoices):
        PENDING = 1, "در انتظار تایید"
        APPROVED = 2, "تایید شده"
        REJECTED = 3, "رد شده"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name="کاربر"
    )
    first_name = models.CharField(max_length=100, blank=True, verbose_name="نام")
    last_name = models.CharField(max_length=100, blank=True, verbose_name="نام خانوادگی")
    seller_request_status = models.PositiveSmallIntegerField(
        choices=SellerRequestStatus.choices,
        default=None,
        null=True,
        blank=True,
        verbose_name="وضعیت درخواست فروشندگی"
    )
    
    class Meta:
        verbose_name = "پروفایل"
        verbose_name_plural = "پروفایل‌ها"

    def __str__(self):
        return f'پروفایل {self.user.email}'

class Address(BaseModel):
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='addresses',
        verbose_name="کاربر"
    )
    province = models.CharField(max_length=100, verbose_name="استان")
    city = models.CharField(max_length=100, verbose_name="شهر")
    street = models.TextField(verbose_name="آدرس دقیق")
    postal_code = models.CharField(max_length=10, verbose_name="کد پستی")

    class Meta:
        verbose_name = "آدرس"
        verbose_name_plural = "آدرس‌ها"
        ordering = ['-created_at']

    def __str__(self):
        return f'آدرس {self.user.email} در {self.city}'
