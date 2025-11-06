from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from apps.core.models import (
    SoftDeleteModel,
    SoftDeleteManager,
    HardDeleteManager,
)


class UserManager(BaseUserManager, SoftDeleteManager):
    def create_user(self, email, phone, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        if not phone:
            raise ValueError("Phone is required")
        email = self.normalize_email(email)
        user = self.model(email=email, phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        user = self.create_user(email, phone, password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save(using=self._db)
        return user


class User(SoftDeleteModel, AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    is_seller = models.BooleanField(default=False)
    picture = models.ImageField(upload_to="users/pictures/", null=True, blank=True)
    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["email", "first_name", "last_name"]
    objects = UserManager()

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.full_name}"


class HardDeleteUser(User):
    objects = HardDeleteManager()

    class Meta:
        proxy = True
        verbose_name = "deleted user"
        verbose_name_plural = "deleted users"
