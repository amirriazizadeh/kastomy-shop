from rest_framework import serializers
from apps.stores.models import Store, StoreItem
from apps.products.serializers import ProductReadSerializer
from apps.products.models import Product


class StoreReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = [
            "id",
            "seller",
            "name",
            "description",
        ]
        read_only_fields = fields


class StoreWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = [
            "name",
            "description",
        ]


class StoreItemSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreItem
        fields = ["id", "store", "stock", "price", "discount", "total_price"]


class StoreItemReadSerializer(serializers.ModelSerializer):
    product = ProductReadSerializer(read_only=True)

    class Meta:
        model = StoreItem
        fields = [
            "id",
            "store",
            "product",
            "stock",
            "is_active",
            "price",
            "discount",
            "total_price",
        ]
        read_only_fields = fields


class StoreItemWriteSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), write_only=True
    )

    class Meta:
        model = StoreItem
        fields = [
            "product",
            "price",
            "discount",
            "stock",
            "is_active",
        ]
