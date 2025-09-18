from django.conf import settings
from django.db import models
from core.models import BaseModel
from django.contrib.auth.models import BaseUserManager,AbstractBaseUser,PermissionsMixin


class UserManager(BaseUserManager):
    def create_user(self, phone_number, email, password=None, **extra_fields):
        
        if not phone_number:
            raise ValueError('The Phone Number field must be set')
        if not email:
            raise ValueError('The Email field must be set')
            
        email = self.normalize_email(email)
        user = self.model(
 
            phone_number=phone_number, 
            email=email, 
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields['role'] = CustomUser.Role.ADMIN
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
            
        return self.create_user( phone_number, email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    
    class Role(models.TextChoices):
        CUSTOMER = 'CUSTOMER', 'مشتری'
        SELLER = 'SELLER', 'فروشگاه'
        ADMIN = 'ADMIN', 'مدیر'

    
    phone_number = models.CharField(max_length=15, unique=True, db_index=True, verbose_name="شماره تلفن")
    email = models.EmailField(unique=True, verbose_name="آدرس ایمیل")
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.CUSTOMER, verbose_name="نقش کاربر")
    is_active = models.BooleanField(default=False, verbose_name="فعال") 
    is_staff = models.BooleanField(default=False, verbose_name="وضعیت کارمند")
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/%Y/%m/', blank=True, null=True)
    is_seller = models.BooleanField(default=False,verbose_name='فروشنده ای؟')
    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['email']

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
    label = models.CharField(max_length=255, verbose_name="عنوان آدرس")
    address_line_1 = models.CharField(max_length=255, verbose_name="آدرس (خط اول)")
    address_line_2 = models.CharField(max_length=255, blank=True, null=True, verbose_name="آدرس (خط دوم)")
    city = models.CharField(max_length=100, verbose_name="شهر")
    state = models.CharField(max_length=100, verbose_name="استان/ایالت")
    postal_code = models.CharField(max_length=20, verbose_name="کد پستی")
    country = models.CharField(max_length=100, verbose_name="کشور")

    class Meta:
        verbose_name = "آدرس"
        verbose_name_plural = "آدرس‌ها"
        

    def __str__(self):
        return f'{self.label} - {self.user.first_name}'