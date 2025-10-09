from django.db import models
from core.models import BaseModel
from django.utils.text import slugify
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Category(BaseModel):
    name = models.CharField(max_length=100, verbose_name="نام دسته‌بندی")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")
    image = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name="تصویر")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='children',
        blank=True,
        null=True,
        verbose_name="دسته والد"
    )

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"
        ordering = ['name']

    def __str__(self):
        return self.name







class Product(BaseModel):
    name = models.CharField(max_length=255, verbose_name="نام محصول")
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True, db_index=True, verbose_name="اسلاگ")
    description = models.TextField(verbose_name="توضیحات")

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='products',
        verbose_name="دسته‌بندی"
    )

    best_seller = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='best_seller_products',
        verbose_name="فروشنده برتر"
    )

    cover_image = models.ImageField(
        upload_to='product_covers/',
        null=True,
        blank=True,
        verbose_name="تصویر کاور"
    )

    stock = models.PositiveIntegerField(
        default=0,
        verbose_name="موجودی انبار"
    )

    best_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="بهترین قیمت"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال"
    )

    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="امتیاز"
    )

    class Meta:
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)
























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
    
    name = models.CharField(default="ویژگی",max_length=100, unique=True, verbose_name="نام ویژگی")
    
    class Meta:
        verbose_name = "ویژگی"
        verbose_name_plural = "ویژگی‌ها"
        ordering = ['name']

    def __str__(self):
        return self.name

class AttributeValue(BaseModel):
    
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name='values', verbose_name="ویژگی")
    value = models.CharField(default="فاقد ویژگی",max_length=100, verbose_name="مقدار")
    
    class Meta:
        verbose_name = "مقدار ویژگی"
        verbose_name_plural = "مقادیر ویژگی‌ها"
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



