from rest_framework import serializers
from .models import (
    Product, Category, ProductImage, 
    Attribute, AttributeValue, ProductVariant
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'slug']

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['image', 'alt_text']


class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = ['name']

class AttributeValueSerializer(serializers.ModelSerializer):
    # To show the attribute name like "Color" instead of just its ID
    attribute = AttributeSerializer(read_only=True)

    class Meta:
        model = AttributeValue
        fields = ['attribute', 'value']

class ProductVariantSerializer(serializers.ModelSerializer):
    attributes = AttributeValueSerializer(many=True, read_only=True)
    name = serializers.CharField(read_only=True)

    class Meta:
        model = ProductVariant
        fields = ['id', 'name', 'attributes']


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 
            'name', 
            'slug', 
            'description', 
            'cover_image',
            'category',
            'images',
            'variants'  
        ]

