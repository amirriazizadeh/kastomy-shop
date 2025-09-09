from django.db import models
from core.models import BaseModel
from shops.models import Shop

class Category(BaseModel):
    """
    Represents a product category, which can be hierarchical.
    """
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Product(BaseModel):
    """
    Represents a generic, base product. It is not tied to any shop.
    It holds the common information like name, description, and images.
    """
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True)
    description = models.TextField()
    cover_image = models.ImageField(upload_to='product_covers/')
    
    def __str__(self):
        return self.name

class ProductImage(BaseModel):
    """
    Stores an individual image for a generic product.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')
    alt_text = models.CharField(max_length=255, blank=True, help_text="Description of the image")

    def __str__(self):
        return f"Image for {self.product.name}"

class Attribute(BaseModel):
    """
    Represents a product attribute type, e.g., 'Color', 'Size'.
    """
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class AttributeValue(BaseModel):
    """
    Represents a specific value for an attribute, e.g., 'Red' for 'Color'.
    """
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name='values')
    value = models.CharField(max_length=100)
    def __str__(self):
        return f"{self.attribute.name}: {self.value}"

class ProductVariant(BaseModel):
    """
    Represents a specific variant of a generic product, combining different attributes.
    e.g., A 'T-shirt' (Product) can have a 'Red, XL' variant.
    This model does NOT contain price or stock.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    attributes = models.ManyToManyField(AttributeValue, related_name='variants')
    
    class Meta:
        unique_together = ('product',) # This will need to be more complex if attributes are used

    def __str__(self):
        return f"Variant of {self.product.name}"

class StoreItem(BaseModel):
    """
    The central model connecting a ProductVariant to a Shop.
    This represents the actual item that is sellable by a store.
    It holds the store-specific price, stock, and SKU.
    THIS is what gets added to the cart.
    """
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='store_items')
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='store_items')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=100, blank=True, help_text="Stock Keeping Unit for this shop")
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('shop', 'variant')

    def __str__(self):
        return f"'{self.variant.product.name}' in shop '{self.shop.name}' for {self.price}"
