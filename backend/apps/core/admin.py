from django.contrib import admin
from django.conf import settings
from django.contrib import messages
from django.utils.translation import gettext_lazy as _



class DeleteHardModelAdmin(admin.ModelAdmin):
    @admin.action(description="Hard delete selected items")
    def hard_delete_selected(self, request, queryset):
        concrete_model = queryset.model._meta.concrete_model
        pks_to_delete = list(queryset.values_list("pk", flat=True))
        deleted_count = len(pks_to_delete)
        concrete_model.all_objects.filter(pk__in=pks_to_delete).delete()
        self.message_user(
            request, f"{deleted_count} items permanently deleted from database"
        )

    @admin.action(description="Restore selected items")
    def restore_selected(self, request, queryset):
        restored_count = 0
        for obj in queryset:
            obj.restore()
            restored_count += 1
        self.message_user(request, f"{restored_count} items restored successfully")

    def get_queryset(self, request):
        return self.model.objects.all()

    def has_add_permission(self, request):
        return False


class SoftDeleteModelAdmin(admin.ModelAdmin):
    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.delete()
        messages.success(
            request, _("Selected items have been soft deleted successfully.")
        )

    def get_actions(self, request):
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            actions["delete_selected"] = (
                self.soft_delete_selected,
                "delete_selected",
                _("Delete selected %(verbose_name_plural)s"),
            )
        return actions

    def soft_delete_selected(self, modeladmin, request, queryset):
        for obj in queryset:
            obj.delete()
        messages.success(request, _("Successfully deleted selected items."))
