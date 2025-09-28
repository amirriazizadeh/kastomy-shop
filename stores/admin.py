from django.contrib import admin
from .models import Store, StoreItem


# -------------------------
# اکشن‌های عمومی برای Logical Delete
# -------------------------
@admin.action(description="حذف منطقی آیتم‌های انتخاب‌شده")
def soft_delete(modeladmin, request, queryset):
    updated = queryset.update(is_deleted=True)
    modeladmin.message_user(request, f"{updated} آیتم به صورت منطقی حذف شدند.")


@admin.action(description="بازگرداندن آیتم‌های انتخاب‌شده")
def restore_items(modeladmin, request, queryset):
    updated = queryset.update(is_deleted=False)
    modeladmin.message_user(request, f"{updated} آیتم بازگردانده شدند.")


# -------------------------
# اکشن‌های فعال/غیرفعال
# -------------------------
@admin.action(description="فعال‌سازی آیتم‌های انتخاب‌شده")
def activate_items(modeladmin, request, queryset):
    updated = queryset.update(is_active=True)
    modeladmin.message_user(request, f"{updated} آیتم فعال شدند.")


@admin.action(description="غیرفعال‌سازی آیتم‌های انتخاب‌شده")
def deactivate_items(modeladmin, request, queryset):
    updated = queryset.update(is_active=False)
    modeladmin.message_user(request, f"{updated} آیتم غیرفعال شدند.")


# -------------------------
# Store Admin
# -------------------------
@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "is_active", "is_deleted", "created_at")
    list_filter = ("is_active", "is_deleted")
    search_fields = ("name", "owner__phone_number", "owner__email")
    actions = [soft_delete, restore_items, activate_items, deactivate_items]

    def has_delete_permission(self, request, obj=None):
        # جلوگیری از حذف فیزیکی
        return False


# -------------------------
# StoreItem Admin
# -------------------------
@admin.register(StoreItem)
class StoreItemAdmin(admin.ModelAdmin):
    list_display = ("store", "variant", "price", "stock_quantity", "is_active", "is_deleted", "created_at")
    list_filter = ("is_active", "is_deleted", "store")
    search_fields = ("store__name", "variant__product__name", "sku")
    actions = [soft_delete, restore_items, activate_items, deactivate_items]

    def has_delete_permission(self, request, obj=None):
        return False
