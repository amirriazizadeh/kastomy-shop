# carts/admin.py
from django.contrib import admin
from django.utils import timezone
from datetime import timedelta
from .models import Cart, CartItem

@admin.action(description="فعال‌سازی سبدهای انتخاب‌شده")
def activate_carts(modeladmin, request, queryset):
    updated = queryset.update(is_active=True)
    modeladmin.message_user(request, f"{updated} سبد خرید فعال شدند.")

@admin.action(description="غیرفعال‌سازی سبدهای انتخاب‌شده")
def deactivate_carts(modeladmin, request, queryset):
    updated = queryset.update(is_active=False)
    modeladmin.message_user(request, f"{updated} سبد خرید غیرفعال شدند.")

@admin.action(description="تمدید تاریخ انقضا (۳ روز دیگر)")
def extend_expiry(modeladmin, request, queryset):
    extended = 0
    for cart in queryset:
        cart.expires_at = timezone.now() + timedelta(days=3)
        cart.save(update_fields=["expires_at"])
        extended += 1
    modeladmin.message_user(request, f"تاریخ انقضا برای {extended} سبد خرید تمدید شد.")


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "total_price", "is_active", "created_at", "expires_at")
    list_filter = ("is_active", "created_at", "expires_at")
    search_fields = ("user__phone_number", "user__email")
    actions = [activate_carts, deactivate_carts, extend_expiry]







@admin.action(description="افزایش تعداد آیتم‌ها (+1)")
def increment_quantity(modeladmin, request, queryset):
    for item in queryset:
        item.quantity += 1
        item.save(update_fields=['quantity'])
    modeladmin.message_user(request, f"{queryset.count()} آیتم تعدادش افزایش یافت.")

@admin.action(description="کاهش تعداد آیتم‌ها (-1)")
def decrement_quantity(modeladmin, request, queryset):
    for item in queryset:
        if item.quantity > 1:
            item.quantity -= 1
            item.save(update_fields=['quantity'])
    modeladmin.message_user(request, f"{queryset.count()} آیتم تعدادش کاهش یافت (حداقل 1).")

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart", "store_item", "quantity", "price", "total_price")
    search_fields = ("cart__user__phone_number", "store_item__variant__product__name")
    actions = [increment_quantity, decrement_quantity]