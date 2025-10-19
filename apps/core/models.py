# add this import at the top of your models.py
from django.utils import timezone
from django.db import models


class BaseModel(models.Model):
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")
    is_deleted = models.BooleanField(default=False, db_index=True, verbose_name="حذف شده")
    # This is the new field to store the deletion timestamp
    deleted_at = models.DateTimeField(null=True, blank=True, editable=False, verbose_name="تاریخ حذف")

    class Meta:
        abstract = True
        ordering = ('-created_at',)
    
    def save(self, *args, **kwargs):
        """
        Overrides the save method to set the deleted_at timestamp
        when an object is soft-deleted, and clear it when it's restored.
        """
        if self.is_deleted and self.deleted_at is None:
            # If the object is being marked as deleted and timestamp is not yet set
            self.deleted_at = timezone.now()
        elif not self.is_deleted and self.deleted_at is not None:
            # If the object is being restored, clear the timestamp
            self.deleted_at = None
            
        super().save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        """
        Soft delete the object by setting is_deleted to True.
        The save() method will handle the deleted_at timestamp.
        """
        self.is_deleted = True
        self.save()

    # def hard_delete(self):
    #     """
    #     Permanently delete the object from the database.
    #     """
    #     super().delete()

    def restore(self):
        """
        Restore a soft-deleted object.
        The save() method will handle clearing the deleted_at timestamp.
        """
        self.is_deleted = False
        self.save()