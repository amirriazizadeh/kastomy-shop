from django.db import models
from core.models import BaseModel
from stores.models import Store
from categories.models import Category

class Product(BaseModel):
    
    name = models.CharField(max_length=255, verbose_name="نام محصول")
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True, db_index=True, verbose_name="اسلاگ")
    description = models.TextField(verbose_name="توضیحات")
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name="دسته‌بندی"
    )
    cover_image = models.ImageField(upload_to='product_covers/', verbose_name="تصویر کاور")

    class Meta:
        verbose_name = "محصول (قالب)"
        verbose_name_plural = "محصولات (قالب‌ها)"
        ordering = ['name']

    def __str__(self):
        return self.name

class ProductImage(BaseModel):
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name="محصول")
    image = models.ImageField(upload_to='product_images/', verbose_name="تصویر")
    alt_text = models.CharField(max_length=255, blank=True, help_text="یک توضیح کوتاه از تصویر برای SEO", verbose_name="متن جایگزین")

    class Meta:
        verbose_name = "تصویر محصول"
        verbose_name_plural = "تصاویر محصول"

    def __str__(self):
        return f"تصویر برای {self.product.name}"

class Attribute(BaseModel):
    
    name = models.CharField(max_length=100, unique=True, verbose_name="نام ویژگی")
    
    class Meta:
        verbose_name = "ویژگی"
        verbose_name_plural = "ویژگی‌ها"
        ordering = ['name']

    def __str__(self):
        return self.name

class AttributeValue(BaseModel):
    
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name='values', verbose_name="ویژگی")
    value = models.CharField(max_length=100, verbose_name="مقدار")
    
    class Meta:
        verbose_name = "مقدار ویژگی"
        verbose_name_plural = "مقادیر ویژگی‌ها"
        constraints = [
            models.UniqueConstraint(fields=['attribute', 'value'], name='unique_attribute_value')
        ]
        ordering = ['attribute__name', 'value']

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"

class ProductVariant(BaseModel):
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants', verbose_name="محصول")
    attributes = models.ManyToManyField(AttributeValue, related_name='variants', verbose_name="ویژگی‌ها")
    
    class Meta:
        verbose_name = "تنوع محصول"
        verbose_name_plural = "تنوع‌های محصول"
        

    @property
    def name(self):
        attributes_qs = self.attributes.select_related('attribute').order_by('attribute__name')
        return " / ".join([attr.value for attr in attributes_qs])

    def __str__(self):
        return f"{self.product.name} ({self.name})"

class StoreItem(BaseModel):
    
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='store_items', verbose_name="فروشگاه")
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='store_items', verbose_name="تنوع محصول")
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="قیمت")
    stock_quantity = models.PositiveIntegerField(default=0, verbose_name="موجودی انبار")
    sku = models.CharField(max_length=100, blank=True, help_text="شناسه انبارداری مختص این فروشگاه", verbose_name="SKU")
    is_active = models.BooleanField(default=True, verbose_name="فعال/غیرفعال")

    class Meta:
        verbose_name = "کالای فروشگاه"
        verbose_name_plural = "کالاهای فروشگاه"
        constraints = [
            models.UniqueConstraint(fields=['store', 'variant'], name='unique_store_variant')
        ]

    def __str__(self):
        return f"کالای '{self.variant}' در فروشگاه '{self.store.name}'"

