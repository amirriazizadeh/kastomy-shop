from django.contrib import admin
from .models import (
    Category, Product, ProductImage,
    Attribute, AttributeValue, ProductVariant
)

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
# Category Admin
# -------------------------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "is_sub", "is_deleted", "created_at")
    list_filter = ("is_sub", "is_deleted")
    search_fields = ("name", "slug")
    actions = [soft_delete, restore_items]

    def has_delete_permission(self, request, obj=None):
        return False


# -------------------------
# Product Admin
# -------------------------
@admin.action(description="فعال‌سازی محصولات انتخاب‌شده")
def activate_products(modeladmin, request, queryset):
    updated = queryset.update(is_active=True)
    modeladmin.message_user(request, f"{updated} محصول فعال شدند.")


@admin.action(description="غیرفعال‌سازی محصولات انتخاب‌شده")
def deactivate_products(modeladmin, request, queryset):
    updated = queryset.update(is_active=False)
    modeladmin.message_user(request, f"{updated} محصول غیرفعال شدند.")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "rating", "is_deleted", "created_at")
    list_filter = ("is_active", "is_deleted", "category")
    search_fields = ("name", "slug", "description")
    actions = [soft_delete, restore_items, activate_products, deactivate_products]

    def has_delete_permission(self, request, obj=None):
        return False


# -------------------------
# ProductImage Admin
# -------------------------
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "alt_text", "is_deleted", "created_at")
    list_filter = ("is_deleted",)
    search_fields = ("product__name", "alt_text")
    actions = [soft_delete, restore_items]

    def has_delete_permission(self, request, obj=None):
        return False


# -------------------------
# Attribute Admin
# -------------------------
@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ("name", "is_deleted", "created_at")
    list_filter = ("is_deleted",)
    search_fields = ("name",)
    actions = [soft_delete, restore_items]

    def has_delete_permission(self, request, obj=None):
        return False


# -------------------------
# AttributeValue Admin
# -------------------------
@admin.register(AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    list_display = ("attribute", "value", "is_deleted", "created_at")
    list_filter = ("attribute", "is_deleted")
    search_fields = ("attribute__name", "value")
    actions = [soft_delete, restore_items]

    def has_delete_permission(self, request, obj=None):
        return False


# -------------------------
# ProductVariant Admin
# -------------------------
@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("product", "name", "is_deleted", "created_at")
    list_filter = ("is_deleted", "product")
    search_fields = ("product__name", "attributes__value")
    actions = [soft_delete, restore_items]

    def has_delete_permission(self, request, obj=None):
        return False
