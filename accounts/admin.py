from django.contrib import admin

# Register your models here.
from .models import CustomUser,Address






from django.contrib import admin
from django.utils import timezone

class SoftDeleteAdmin(admin.ModelAdmin):
    """
    Custom admin class to enable logical delete for models
    that inherit from BaseModel.
    """

    # Optional: to hide logically deleted objects by default
    def get_queryset(self, request):
        # Exclude deleted objects from admin list view
        qs = super().get_queryset(request)
        return qs

    # Override single object delete
    def delete_model(self, request, obj):
        obj.is_deleted = True
        obj.deleted_at = timezone.now()
        obj.save()

    # Override bulk delete action
    def delete_queryset(self, request, queryset):
        queryset.update(is_deleted=True, deleted_at=timezone.now())

    # Optional: add custom action to restore objects
    actions = ["restore_objects"]

    def restore_objects(self, request, queryset):
        queryset.update(is_deleted=False, deleted_at=None)
    restore_objects.short_description = "بازیابی موارد حذف‌شده"





# accounts/admin.py
from django.contrib import admin
from .models import CustomUser

# --- اکشن‌ها ---
@admin.action(description="فعال‌سازی کاربران انتخاب‌شده")
def activate_users(modeladmin, request, queryset):
    updated = queryset.update(is_active=True)
    modeladmin.message_user(request, f"{updated} کاربر فعال شدند.")

@admin.action(description="غیرفعال‌سازی کاربران انتخاب‌شده")
def deactivate_users(modeladmin, request, queryset):
    updated = queryset.update(is_active=False)
    modeladmin.message_user(request, f"{updated} کاربر غیرفعال شدند.")

@admin.action(description="تبدیل به فروشنده")
def make_sellers(modeladmin, request, queryset):
    updated = queryset.update(role=CustomUser.Role.SELLER, is_seller=True)
    modeladmin.message_user(request, f"{updated} کاربر فروشنده شدند.")

@admin.action(description="تبدیل به مشتری")
def make_customers(modeladmin, request, queryset):
    updated = queryset.update(role=CustomUser.Role.CUSTOMER, is_seller=False)
    modeladmin.message_user(request, f"{updated} کاربر مشتری شدند.")


# --- ثبت مدل در ادمین ---
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("phone_number", "email", "role", "is_active", "is_seller")
    list_filter = ("role", "is_active", "is_seller")
    search_fields = ("phone_number", "email", "first_name", "last_name")
    actions = [activate_users, deactivate_users, make_sellers, make_customers]






# addresses/admin.py
from django.contrib import admin
from .models import Address

@admin.action(description="تنظیم به‌عنوان آدرس اصلی")
def make_main(modeladmin, request, queryset):
    for address in queryset:
        Address.objects.filter(user=address.user, is_main=True).update(is_main=False)
        address.is_main = True
        address.save()
    modeladmin.message_user(request, f"{queryset.count()} آدرس به عنوان اصلی تنظیم شدند.")

@admin.action(description="حذف منطقی آدرس‌های انتخاب‌شده")
def soft_delete_addresses(modeladmin, request, queryset):
    updated = queryset.update(is_deleted=True)
    modeladmin.message_user(request, f"{updated} آدرس حذف منطقی شدند.")

@admin.action(description="بازیابی آدرس‌های حذف‌شده")
def restore_addresses(modeladmin, request, queryset):
    updated = queryset.update(is_deleted=False)
    modeladmin.message_user(request, f"{updated} آدرس بازیابی شدند.")

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("label", "user", "city", "state", "is_main", "is_deleted")
    list_filter = ("city", "state", "is_main", "is_deleted")
    search_fields = ("label", "address_line_1", "postal_code", "user__phone_number")
    actions = [make_main, soft_delete_addresses, restore_addresses]

    def get_queryset(self, request):
        # پیش‌فرض: فقط آدرس‌های حذف‌نشده نمایش داده شود
        return super().get_queryset(request)
