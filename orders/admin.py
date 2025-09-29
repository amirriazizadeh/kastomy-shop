from django.contrib import admin

# Register your models here.
from .models import Order,OrderItem,Discount,DiscountUsage


admin.site.register(Discount)
admin.site.register(DiscountUsage)



from django.contrib import admin
from .models import Order


@admin.action(description="تأیید سفارش‌های انتخاب‌شده")
def approve_orders(modeladmin, request, queryset):
    updated = queryset.filter(status="pending").update(status="approved")
    modeladmin.message_user(request, f"{updated} سفارش تأیید شدند.")


@admin.action(description="علامت‌گذاری به عنوان پرداخت‌شده")
def mark_as_paid(modeladmin, request, queryset):
    updated = queryset.filter(status__in=["pending", "approved"]).update(status="paid")
    modeladmin.message_user(request, f"{updated} سفارش پرداخت‌شده شدند.")


@admin.action(description="رد کردن سفارش‌های انتخاب‌شده")
def reject_orders(modeladmin, request, queryset):
    updated = queryset.filter(status="pending").update(status="rejected")
    modeladmin.message_user(request, f"{updated} سفارش رد شدند.")


@admin.action(description="بازگرداندن به حالت در انتظار (Pending)")
def reset_to_pending(modeladmin, request, queryset):
    updated = queryset.exclude(status="paid").update(status="pending")
    modeladmin.message_user(request, f"{updated} سفارش به حالت Pending بازگردانده شدند.")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("id", "user__phone_number", "user__email")
    actions = [approve_orders, mark_as_paid, reject_orders, reset_to_pending]

    # ---------------------------
    # مجوزهای مشاهده و تغییر
    # ---------------------------
    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.has_perm("app.view_order")

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.has_perm("app.change_order")

    def has_delete_permission(self, request, obj=None):
        # هیچکس حق حذف سفارش رو نداره
        return False




@admin.action(description="تأیید آیتم‌های انتخاب‌شده (به در حال آماده‌سازی)")
def mark_preparing(modeladmin, request, queryset):
    updated = queryset.filter(status=OrderItem.OrderItemStatus.PENDING).update(
        status=OrderItem.OrderItemStatus.PREPARING
    )
    modeladmin.message_user(request, f"{updated} آیتم به وضعیت 'در حال آماده‌سازی' تغییر کردند.")


@admin.action(description="علامت‌گذاری به عنوان ارسال شده")
def mark_shipped(modeladmin, request, queryset):
    updated = queryset.filter(
        status=OrderItem.OrderItemStatus.PREPARING
    ).update(status=OrderItem.OrderItemStatus.SHIPPED)
    modeladmin.message_user(request, f"{updated} آیتم به وضعیت 'ارسال شده' تغییر کردند.")


@admin.action(description="علامت‌گذاری به عنوان تحویل داده شده")
def mark_delivered(modeladmin, request, queryset):
    updated = queryset.filter(
        status=OrderItem.OrderItemStatus.SHIPPED
    ).update(status=OrderItem.OrderItemStatus.DELIVERED)
    modeladmin.message_user(request, f"{updated} آیتم به وضعیت 'تحویل داده شده' تغییر کردند.")


@admin.action(description="لغو آیتم‌های انتخاب‌شده")
def cancel_items(modeladmin, request, queryset):
    updated = queryset.exclude(status=OrderItem.OrderItemStatus.DELIVERED).update(
        status=OrderItem.OrderItemStatus.CANCELLED
    )
    modeladmin.message_user(request, f"{updated} آیتم لغو شدند.")


@admin.action(description="مرجوع کردن آیتم‌های انتخاب‌شده")
def return_items(modeladmin, request, queryset):
    updated = queryset.filter(status=OrderItem.OrderItemStatus.DELIVERED).update(
        status=OrderItem.OrderItemStatus.RETURNED
    )
    modeladmin.message_user(request, f"{updated} آیتم مرجوع شدند.")


@admin.action(description="بازگرداندن آیتم‌ها به وضعیت در انتظار تایید")
def reset_pending(modeladmin, request, queryset):
    updated = queryset.exclude(status=OrderItem.OrderItemStatus.DELIVERED).update(
        status=OrderItem.OrderItemStatus.PENDING
    )
    modeladmin.message_user(request, f"{updated} آیتم به Pending بازگردانده شدند.")


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "store_item", "quantity", "price", "status", "subtotal")
    list_filter = ("status",)
    search_fields = ("order__id", "store_item__variant__product__name")
    actions = [
        mark_preparing,
        mark_shipped,
        mark_delivered,
        cancel_items,
        return_items,
        reset_pending,
    ]

    def has_delete_permission(self, request, obj=None):
        """حذف آیتم سفارش مجاز نیست"""
        return False
