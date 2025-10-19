# carts/admin.py
from django.contrib import admin
from django.utils import timezone
from datetime import timedelta
from .models import Cart, CartItem



admin.site.register(Cart)
admin.site.register(CartItem)