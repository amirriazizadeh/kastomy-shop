from django.contrib import admin
from stores.models import StoreItem
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

    # فقط کسانی که پرمیشن view_category دارند می‌بینند
    def has_view_permission(self, request, obj=None):
        return request.user.has_perm("app_name.view_category")

    # فقط کسانی که پرمیشن add_category دارند می‌توانند اضافه کنند
    def has_add_permission(self, request):
        return request.user.has_perm("app_name.add_category")

    # فقط کسانی که پرمیشن change_category دارند می‌توانند تغییر دهند
    def has_change_permission(self, request, obj=None):
        return request.user.has_perm("app_name.change_category")

    # فقط کسانی که پرمیشن delete_category دارند می‌توانند حذف کنند
    def has_delete_permission(self, request, obj=None):
        return request.user.has_perm("app_name.delete_category")

    # فیلد is_active را فقط کسانی که can_activate_category دارند بتوانند تغییر دهند
    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))
        if not request.user.has_perm("app_name.can_activate_category"):
            readonly.append("is_active")  # این فیلد فقط خواندنی می‌شود
        return readonly

    # برای زیر دسته‌ها هم می‌توانیم محدودیت بگذاریم
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # فرض: کاربران عادی فقط می‌توانند دسته‌های بدون والد را ببینند
        return qs.filter(parent__isnull=True)


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


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "alt_text", "is_deleted")
    readonly_fields = ("is_deleted",)




class StoreItemInline(admin.TabularInline):
    model = StoreItem
    extra = 1
    fields = ("store", "price", "stock_quantity", "sku", "is_active", "is_deleted")
    readonly_fields = ("is_deleted",)



class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    filter_horizontal = ("attributes",)  
    fields = ("attributes", "is_deleted")
    readonly_fields = ("is_deleted",)



@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "rating", "is_deleted", "created_at")
    list_filter = ("is_active", "is_deleted", "category")
    search_fields = ("name", "slug", "description")
    actions = [soft_delete, restore_items, activate_products, deactivate_products]
    inlines = [ProductImageInline, ProductVariantInline]

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
    actions = [soft_delete, restore_items,]
    inlines = [StoreItemInline]

    def has_delete_permission(self, request, obj=None):
        return False
