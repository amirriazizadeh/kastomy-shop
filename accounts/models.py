from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from core.models import BaseModel

class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("The Phone Number field must be set")
        
        email = extra_fields.get('email')
        if email:
            extra_fields['email'] = self.normalize_email(email)

        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone_number, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model for authentication with phone number or email.
    """
    class Role(models.TextChoices):
        CUSTOMER = 'CUSTOMER', 'Customer'
        SELLER = 'SELLER', 'Seller'
        ADMIN = 'ADMIN', 'Admin'

    phone_number = models.CharField(max_length=15, unique=True, verbose_name="Phone Number")
    email = models.EmailField(unique=True, null=True, blank=True, verbose_name="Email Address")
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.CUSTOMER, verbose_name="User Role")
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    def __str__(self):
        return self.phone_number

class Profile(BaseModel):
    """
    Stores additional information and seller request status for a user.
    """
    class SellerStatus(models.TextChoices):
        NONE = 'NONE', 'None'
        PENDING = 'PENDING', 'Pending Approval'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    seller_status = models.CharField(max_length=10, choices=SellerStatus.choices, default=SellerStatus.NONE)

    def __str__(self):
        return f"Profile of {self.user.phone_number}"

class Address(BaseModel):
    """
    Represents a shipping address for a user. A user can have multiple addresses.
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='addresses')
    province = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    address_detail = models.TextField()
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"Address for {self.user.phone_number} in {self.city}"

class OTP(BaseModel):
    """
    Stores One-Time Passwords for phone number verification.
    """
    phone_number = models.CharField(max_length=15)
    code = models.CharField(max_length=6)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"OTP {self.code} for {self.phone_number}"
