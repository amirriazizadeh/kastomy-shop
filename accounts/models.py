from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from core.models import BaseModel


class UserManager(BaseUserManager):
    
    def create_user(self, phone_number, password=None, **extra_fields):
        
        if not phone_number:
            raise ValueError("The Phone Number field must be set")

        if 'email' in extra_fields and extra_fields['email']:
            extra_fields['email'] = self.normalize_email(extra_fields['email'])

        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', CustomUser.Role.ADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        if extra_fields.get('role') != CustomUser.Role.ADMIN:
            raise ValueError('Superuser must have role of ADMIN.')

        return self.create_user(phone_number, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    
    class Role(models.TextChoices):
        CUSTOMER = 'CUSTOMER', 'مشتری'
        SELLER = 'SELLER', 'فروشگاه'
        ADMIN = 'ADMIN', 'مدیر'

    phone_number = models.CharField(max_length=15, unique=True, db_index=True, verbose_name="شماره تلفن")
    email = models.EmailField(unique=True, null=True, blank=True, verbose_name="آدرس ایمیل")
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.CUSTOMER, verbose_name="نقش کاربر")

    is_active = models.BooleanField(default=False, verbose_name="فعال")
    is_staff = models.BooleanField(default=False, verbose_name="وضعیت کارمند")
    
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)

    profile_picture = models.ImageField(upload_to='profiles/%Y/%m/', blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"

    def __str__(self):
        return self.phone_number

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