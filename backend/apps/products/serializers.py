from rest_framework import serializers
from apps.products.models import Product, ProductImage
from apps.categories.serializers import CategorySimpleSerializer
from apps.categories.models import Category
from apps.users.serializers_base import UserSimpleSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ["id", "image_url"]

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image:
            return (
                request.build_absolute_uri(obj.image.url) if request else obj.image.url
            )
        return None


class ProductReadSerializer(serializers.ModelSerializer):
    category = CategorySimpleSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    best_price = serializers.ReadOnlyField()
    sellers = serializers.SerializerMethodField()
    best_seller = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "is_active",
            "category",
            "rating",
            "images",
            "stock",
            "best_price",
            "sellers",
            "best_seller",
        ]
        read_only_fields = fields

    def get_sellers(self, obj):
        store_items = obj.store_items.all()
        return [
            {
                "store": {
                    "id": si.store.id if si.store else None,
                    "name": si.store.name if si.store else None,
                },
                "id": si.id,
                "price": si.price,
                "discount_price": si.total_price,
                "stock": si.stock,
                "product": obj.id,
            }
            for si in store_items
        ]

    def get_best_seller(self, obj):
        si = obj.store_items.all().order_by("-stock").first()
        if not si:
            return None
        return {
            "store": {
                "id": si.store.id if si.store else None,
                "name": si.store.name if si.store else None,
            },
            "id": si.id,
            "price": si.price,
            "discount_price": si.total_price,
            "stock": si.stock,
            "product": obj.id,
        }


class ProductWriteSerializer(serializers.ModelSerializer):
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source="category", write_only=True
    )
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(
            max_length=1000000, allow_empty_file=False, use_url=False
        ),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Product
        fields = [
            "name",
            "description",
            "is_active",
            "category_id",
            "uploaded_images",
            "stock",
        ]

    def create(self, validated_data):
        uploaded_images = validated_data.pop("uploaded_images", [])
        product = Product.objects.create(**validated_data)
        for image in uploaded_images:
            ProductImage.objects.create(product=product, image=image)
        return product

    def update(self, instance, validated_data):
        uploaded_images = validated_data.pop("uploaded_images", [])
        instance = super().update(instance, validated_data)
        for image in uploaded_images:
            ProductImage.objects.create(product=instance, image=image)
        return instance
