from django.conf import settings
from django.db import models
from core.models import BaseModel
from django.contrib.auth.models import BaseUserManager,AbstractBaseUser,PermissionsMixin
from django.core.validators import RegexValidator




class UserManager(BaseUserManager):
        
    def create_user(self, username, email, phone, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        if not email:
            raise ValueError('The Email field must be set')
        if not phone:
            raise ValueError('The Phone field must be set')

        email = self.normalize_email(email)
        user = self.model(
            username=username,
            email=email,
            phone=phone,
            **extra_fields
        )
        user.set_password(password)

        # اگر status داده نشده بود، پیش‌فرض 'inactive' بذار
        if 'status' not in extra_fields:
            user.status = 'inactive'

        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('status', 'active')  # سوپر یوزر همیشه فعال

        return self.create_user(username, email, phone, password, **extra_fields)






class CustomUser(AbstractBaseUser, PermissionsMixin):
    
    phone_validator = RegexValidator(
        regex=r'^09\d{9}$',
        message="شماره تلفن باید با فرمت '09123456789' وارد شود."
    )

    username = models.CharField(max_length=150, unique=True, verbose_name="نام کاربری")
    status = models.CharField(max_length=20, default='inactive', verbose_name="وضعیت")
    email = models.EmailField(unique=True, verbose_name="ایمیل")
    first_name = models.CharField(max_length=150, blank=True, verbose_name="نام")
    last_name = models.CharField(max_length=150, blank=True, verbose_name="نام خانوادگی")

    phone = models.CharField(
        max_length=15,
        unique=True,
        db_index=True,
        validators=[phone_validator],
        verbose_name="شماره تلفن"
    )
    is_seller = models.BooleanField(default=False, verbose_name="فروشنده است؟")
    picture = models.ImageField(upload_to='profiles/%Y/%m/', blank=True, null=True, verbose_name="عکس پروفایل")
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)


    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'phone']

    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"

    def __str__(self):
        return self.username or self.phone

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
    postal_code = models.CharField(unique=True,max_length=20, verbose_name="کد پستی")
    country = models.CharField(max_length=100, verbose_name="کشور")
    is_main = models.BooleanField(default=False, verbose_name="آدرس اصلی")

    class Meta:
        verbose_name = "آدرس"
        verbose_name_plural = "آدرس‌ها"

    def __str__(self):
        return f'{self.label} - {self.user.first_name}'

    def save(self, *args, **kwargs):
        if not self.pk:
            Address.objects.filter(user=self.user, is_main=True).update(is_main=False)
            self.is_main = True
            
        super(Address, self).save(*args, **kwargs)