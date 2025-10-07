from rest_framework import serializers
from .models import (
    Product, Category, ProductImage, 
    Attribute, AttributeValue, ProductVariant
)

from rest_framework import serializers
from .models import Product, ProductImage, Category
from accounts.models import CustomUser  # فروشنده



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



# -------------------------------
# 🔸 ProductImage Serializer
# -------------------------------
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']


# -------------------------------
# 🔸 Seller Serializer (نمایش فروشنده)
# -------------------------------
class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'phone', 'email']
        read_only_fields = fields




# -------------------------------
# 🔸 Category Serializer 
# -------------------------------

class CategorySimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class CategorySerializer(serializers.ModelSerializer):
    children = CategorySimpleSerializer(many=True, read_only=True)
    parents = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'id', 'image', 'name', 'description',
            'is_active', 'parent', 'children', 'parents'
        ]

    def get_parents(self, obj):
        """بازگرداندن لیست والدها تا بالاترین سطح"""
        parents = []
        current = obj.parent
        while current:
            parents.insert(0, current)  # از بالا به پایین مرتب کنیم
            current = current.parent
        return CategorySimpleSerializer(parents, many=True).data





# -------------------------------
# 🔸 Product Serializer اصلی
# -------------------------------
class ProductSerializer(serializers.ModelSerializer):
    category = CategorySimpleSerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )

    best_seller = SellerSerializer(read_only=True)
    best_seller_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),  # ✅ بدون فیلتر role
        source='best_seller',
        write_only=True,
        required=False,
        allow_null=True
    )

    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'description',
            'rating',
            'stock',
            'best_seller',
            'best_seller_id',
            'best_price',
            'category',
            'category_id',
            'images',
            'is_active',
        ]

    def create(self, validated_data):
        """
        ساخت محصول جدید + آپلود چند تصویر در صورت ارسال
        """
        images_data = self.context['request'].FILES.getlist('images')
        product = super().create(validated_data)
        for img in images_data:
            ProductImage.objects.create(product=product, image=img)
        return product

    def update(self, instance, validated_data):
        """
        آپدیت محصول + تعویض تصاویر (در صورت ارسال جدید)
        """
        images_data = self.context['request'].FILES.getlist('images')
        instance = super().update(instance, validated_data)
        if images_data:
            instance.images_list.all().delete()
            for img in images_data:
                ProductImage.objects.create(product=instance, image=img)
        return instance