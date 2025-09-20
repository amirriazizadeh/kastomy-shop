from rest_framework import serializers
from .models import (
    Product, Category, ProductImage, 
    Attribute, AttributeValue, ProductVariant
)


class RecursiveField(serializers.Serializer):
    
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data

class CategorySerializer(serializers.ModelSerializer):
    
    children = RecursiveField(many=True, read_only=True)

    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'slug',
            'parent', 
            'children' 
        ]


class CategoryCreateUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Category
        fields = [
            'name',
            'slug',
            'parent',
        ]
    
    def validate_parent(self, value):
        if self.instance and value == self.instance:
            raise serializers.ValidationError("یک دسته‌بندی نمی‌تواند والد خودش باشد.")
        return value

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
    category = CategorySerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'cover_image',
            'is_active', 'rating', 'category', 'images', 'variants'
        ]

class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        many=True,
        allow_empty=False 
    )

    class Meta:
        model = Product
        fields = [
            'name',
            'slug',
            'description',
            'cover_image',
            'is_active',
            'category' 
        ]