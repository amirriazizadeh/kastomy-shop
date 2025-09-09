from django.db import models

class SoftDeleteManager(models.Manager):
    """
    Custom manager to automatically filter out objects that are soft-deleted.
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class BaseModel(models.Model):
    """
    An abstract base model providing common fields for all other models.

    Fields:
        - created_at: DateTimeField, automatically set when the object is first created.
        - updated_at: DateTimeField, automatically set every time the object is saved.
        - is_deleted: BooleanField, used for logical deletion instead of physical deletion.
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")
    is_deleted = models.BooleanField(default=False, verbose_name="Is Deleted")

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def soft_delete(self):
        """Marks the instance as deleted."""
        self.is_deleted = True
        self.save()

    def restore(self):
        """Restores a soft-deleted instance."""
        self.is_deleted = False
        self.save()
