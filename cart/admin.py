from django.contrib import admin
from django.utils import timezone

from .models import Cart,CartItem



admin.site.register(Cart)
admin.site.register(CartItem)