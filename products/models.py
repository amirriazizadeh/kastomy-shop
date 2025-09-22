from django.db import models
from core.models import BaseModel


from django.db import models
from core.models import BaseModel

class Category(BaseModel):
    
    name = models.CharField(unique=True,max_length=200, verbose_name="نام دسته‌بندی")
    slug = models.SlugField(max_length=250, unique=True, allow_unicode=True, verbose_name="اسلاگ")
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
        verbose_name="دسته‌بندی والد"
    )
    is_sub = models.BooleanField(default=False)

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"

    def __str__(self):
        return self.name


class Product(BaseModel):
    
    name = models.CharField(max_length=255, verbose_name="نام محصول")
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True, db_index=True, verbose_name="اسلاگ")
    description = models.TextField(verbose_name="توضیحات")
    category = models.ManyToManyField(
        Category,
        related_name='products',
        verbose_name="دسته‌بندی"
    )
    cover_image = models.ImageField(upload_to='product_covers/', verbose_name="تصویر کاور")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True, verbose_name="امتیاز")

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



