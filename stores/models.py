from django.db import models
from django.conf import settings
from core.models import BaseModel
# from products.models import ProductVariant
from accounts.models import Address

class Store(BaseModel):
    
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='store',
        verbose_name="مالک فروشگاه"
    )
    name = models.CharField(max_length=200, unique=True, verbose_name="نام فروشگاه")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    address = models.ForeignKey(Address,on_delete=models.PROTECT,verbose_name='آدرس')
    is_active = models.BooleanField(default=False, verbose_name="فعال")

    class Meta:
        verbose_name = "فروشگاه"
        verbose_name_plural = "فروشگاه‌ها"
        permissions = [
            ("can_activate_store", "Can activate/deactivate store"),   # فعال/غیرفعال کردن فروشگاه
            ("can_manage_store_owner", "Can change store owner"),      # تغییر مالک فروشگاه
            ("can_edit_store_address", "Can edit store address"),      # تغییر آدرس فروشگاه
            ("can_manage_store_info", "Can manage store info"),        # ویرایش نام و توضیحات فروشگاه
        ]

    def __str__(self):
        return self.name
    
class StoreItem(BaseModel):
    
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='store_items', verbose_name="فروشگاه")
    variant = models.ForeignKey('products.ProductVariant', on_delete=models.CASCADE, related_name='store_items', verbose_name="تنوع محصول")
    price = models.DecimalField(max_digits=12, decimal_places=2,null=False,blank=False, verbose_name="قیمت")
    stock = models.PositiveIntegerField(default=0, verbose_name="موجودی انبار")
    sku = models.CharField(max_length=100, blank=True, help_text="شناسه انبارداری مختص این فروشگاه", verbose_name="SKU")
    is_active = models.BooleanField(default=True, verbose_name="فعال/غیرفعال")

    class Meta:
        verbose_name = "کالای فروشگاه"
        verbose_name_plural = "کالاهای فروشگاه"
        permissions = [
            ("can_activate_item", "Can activate/deactivate store item"),      # فعال یا غیرفعال کردن کالا
            ("can_edit_price", "Can edit store item price"),                  # ویرایش قیمت کالا
            ("can_edit_stock", "Can edit stock quantity"),                    # تغییر موجودی انبار
            ("can_manage_sku", "Can manage SKU for store item"),              # مدیریت SKU
        ]
        

    def __str__(self):
        return f"کالای '{self.variant}' در فروشگاه '{self.store.name}'"