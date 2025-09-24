from django.contrib import admin

from .models import Product,ProductImage,ProductVariant,Attribute,AttributeValue,Category


admin.site.register(Category)
admin.site.register(ProductImage)
admin.site.register(ProductVariant)
admin.site.register(Attribute)
admin.site.register(AttributeValue)



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



@admin.register(Product)
class ProductAdmin(SoftDeleteAdmin):
    list_display = ('name', )
    list_filter = ('name',)
    search_fields = ('name',)



