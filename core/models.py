from django.db import models


class BaseModel(models.Model):
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")
    is_deleted = models.BooleanField(default=False, db_index=True, verbose_name="حذف شده")

    class Meta:
        abstract = True
        ordering = ('-created_at',)

    def delete(self, using=None, keep_parents=False):
        
        self.is_deleted = True
        self.save()

    def hard_delete(self):
        super().delete()

    def restore(self):
        self.is_deleted = False
        self.save()
