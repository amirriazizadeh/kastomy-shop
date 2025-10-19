from rest_framework import serializers
from .models import CartItem,Cart
from apps.products.serializers import ProductSerializer

from apps.products.models import Product
from apps.stores.models import Store,StoreItem
from apps.products.serializers import ProductImageSerializer


# --- Store Serializers ---
class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ["id", "name", "description", "seller", ]


# --- StoreItem Serializers ---
class StoreItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = StoreItem
        fields = [
            "id",
            "price",
            "discount_price",
            "stock",
            "is_active",
            "created_at",
            "updated_at",
            "product",
            "store",
        ]


# --- CartItem Serializers ---
class CartItemSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    store = serializers.SerializerMethodField()
    store_item = StoreItemSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product",
            "quantity",
            "store",
            "total_item_price",
            "total_discount",
            "total_price",
            "unit_price",
            "store_item",
        ]

    def get_product(self, obj):
        product = obj.store_item.product
        return ProductSerializer(product).data


    def get_store(self, obj):
        if obj.store_item and obj.store_item.store:
            return StoreSerializer(obj.store_item.store).data
        return None


# --- Cart Serializer ---
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "user", "items", "total_price", "total_discount", "is_active"]
        read_only_fields = ["user", "total_price", "total_discount", "is_active"]

    def create(self, validated_data):
        user = self.context["request"].user
        cart = Cart.objects.create(user=user)
        return cart