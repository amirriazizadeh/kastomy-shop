from django.db import models
from django.conf import settings
from core.models import BaseModel

class Shop(BaseModel):
    """
    Represents a seller's shop in the multi-store system.
    """
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='shop', 
        limit_choices_to={'role': 'SELLER'}
    )
    name = models.CharField(max_length=255, verbose_name="Shop Name")
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='shop_logos/', blank=True, null=True)
    is_active = models.BooleanField(default=True, help_text="Is the shop approved and active?")
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    
    contact_phone = models.CharField(max_length=20, blank=True)
    province = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    address_detail = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Shop"
        verbose_name_plural = "Shops"

    def __str__(self):
        return self.name
