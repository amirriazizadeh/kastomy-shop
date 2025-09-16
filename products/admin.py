from django.contrib import admin

from .models import Product,ProductImage,ProductVariant,Attribute,AttributeValue,Category

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(ProductImage)
admin.site.register(ProductVariant)
admin.site.register(Attribute)
admin.site.register(AttributeValue)