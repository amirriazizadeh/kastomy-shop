from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    """
    Abstract base model with common fields and logical delete
    """
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, db_index=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def delete(self, using=None, keep_parents=False):
        """
        Logical delete: mark the record as deleted instead of removing it
        """
        self.is_deleted = True
        self.save(using=using)

    def hard_delete(self, using=None, keep_parents=False):
        """
        Permanently delete the record from the database
        """
        super().delete(using=using, keep_parents=keep_parents)
