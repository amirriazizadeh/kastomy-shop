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




class CartItemInline(admin.TabularInline): 
    model = CartItem
    extra = 1  
    fields = ("store_item", "quantity", "price", "total_price")
    readonly_fields = ("total_price",)  

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "total_price", "is_active", "created_at", "expires_at")
    list_filter = ("is_active", "created_at", "expires_at")
    search_fields = ("user__phone_number", "user__email")
    actions = [activate_carts, deactivate_carts, extend_expiry]
    inlines = [CartItemInline]

    # # فقط کسانی که پرمیشن view_cart دارند می‌بینند
    # def has_view_permission(self, request, obj=None):
    #     return request.user.has_perm("app_name.view_cart") 

    # # فقط کسانی که پرمیشن add_cart دارند می‌توانند اضافه کنند
    # def has_add_permission(self, request):
    #     return request.user.has_perm("app_name.add_cart")

    # # فقط کسانی که پرمیشن change_cart دارند می‌توانند تغییر دهند
    # def has_change_permission(self, request, obj=None):
    #     return request.user.has_perm("app_name.change_cart")

    # # فقط کسانی که پرمیشن delete_cart دارند می‌توانند حذف کنند
    # def has_delete_permission(self, request, obj=None):
    #     return request.user.has_perm("app_name.delete_cart")

# ////////////////////////////////////////////////////////////////////////////////




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

    # فیلتر کردن آیتم‌ها بر اساس صاحب سبد
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs  # ادمین همه چیز رو می‌بینه
        return qs.filter(cart__user=request.user)  # فقط آیتم‌های سبد خودش

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        # فقط آیتم‌های سبد خودش رو ببینه
        return obj is None or obj.cart.user == request.user

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return obj is not None and obj.cart.user == request.user

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return obj is not None and obj.cart.user == request.user

    def has_add_permission(self, request):
        # اگه خواستی کاربر خودش آیتم به سبدش اضافه کنه، True بذار
        return True
