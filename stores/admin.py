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
class StoreItemInline(admin.TabularInline): 
    model = StoreItem
    extra = 1 


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    inlines = [StoreItemInline]
    list_display = ("name", "owner", "is_active", "is_deleted", "created_at")
    list_filter = ("is_active", "is_deleted")
    search_fields = ("name", "owner__phone_number", "owner__email")
    actions = [soft_delete, restore_items, activate_items, deactivate_items]


    # فقط کسانی که پرمیشن view_store دارند می‌بینند
    def has_view_permission(self, request, obj=None):
        return request.user.has_perm("app_name.view_store")

    # فقط کسانی که پرمیشن add_store دارند می‌توانند اضافه کنند
    def has_add_permission(self, request):
        return request.user.has_perm("app_name.add_store")

    # فقط کسانی که پرمیشن change_store دارند می‌توانند تغییر دهند
    def has_change_permission(self, request, obj=None):
        return request.user.has_perm("app_name.change_store")

    # فقط کسانی که پرمیشن delete_store دارند می‌توانند حذف کنند
    def has_delete_permission(self, request, obj=None):
        return request.user.has_perm("app_name.delete_store")

    # کنترل دسترسی به فیلدها بر اساس پرمیشن‌های سفارشی
    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))

        # فیلد is_active فقط برای کسانی که can_activate_store دارند
        if not request.user.has_perm("app_name.can_activate_store"):
            readonly.append("is_active")

        # فیلد owner فقط برای کسانی که can_manage_store_owner دارند
        if not request.user.has_perm("app_name.can_manage_store_owner"):
            readonly.append("owner")

        # فیلدهای name و description فقط برای کسانی که can_manage_store_info دارند
        if not request.user.has_perm("app_name.can_manage_store_info"):
            readonly.extend(["name", "description"])

        # فیلد address فقط برای کسانی که can_edit_store_address دارند
        if not request.user.has_perm("app_name.can_edit_store_address"):
            readonly.append("address")

        return readonly


# -------------------------
# StoreItem Admin
# -------------------------
@admin.register(StoreItem)
class StoreItemAdmin(admin.ModelAdmin):
    list_display = ("store", "variant", "price", "stock_quantity", "is_active", "is_deleted", "created_at")
    list_filter = ("is_active", "is_deleted", "store")
    search_fields = ("store__name", "variant__product__name", "sku")
    actions = [soft_delete, restore_items, activate_items, deactivate_items]

    # متدهای پیش‌فرض پرمیشن
    def has_view_permission(self, request, obj=None):
        return request.user.has_perm("app_name.view_storeitem")

    def has_add_permission(self, request):
        return request.user.has_perm("app_name.add_storeitem")

    def has_change_permission(self, request, obj=None):
        return request.user.has_perm("app_name.change_storeitem")

    def has_delete_permission(self, request, obj=None):
        return request.user.has_perm("app_name.delete_storeitem")

    # محدود کردن فیلدها بر اساس پرمیشن‌های سفارشی
    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))

        if not request.user.has_perm("app_name.can_activate_item"):
            readonly.append("is_active")

        if not request.user.has_perm("app_name.can_edit_price"):
            readonly.append("price")

        if not request.user.has_perm("app_name.can_edit_stock"):
            readonly.append("stock_quantity")

        if not request.user.has_perm("app_name.can_manage_sku"):
            readonly.append("sku")

        return readonly

    # فیلتر کردن queryset برای مالک فروشگاه یا سوپر یوزر
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # فرض: مالک فروشگاه فقط آیتم‌های فروشگاه خودش را می‌بیند
        return qs.filter(store__owner=request.user)
