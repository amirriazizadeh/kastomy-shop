from rest_framework import serializers
from apps.orders.models import Order, OrderItem
from apps.addresses.serializers import AddressReadSerializer
from apps.stores.serializers import StoreItemReadSerializer
from apps.users.serializers_base import UserSimpleSerializer
from apps.products.serializers import ProductReadSerializer


class OrderItemReadSerializer(serializers.ModelSerializer):
    store_item = StoreItemReadSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "store_item", "quantity", "price", "total_price"]
        read_only_fields = fields


class OrderReadSerializer(serializers.ModelSerializer):
    customer = UserSimpleSerializer(read_only=True)
    address = AddressReadSerializer(read_only=True)
    items = OrderItemReadSerializer(many=True, read_only=True)
    discount_price = serializers.DecimalField(
        source="total_price",
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )
    products = serializers.SerializerMethodField()
    store = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "customer",
            "address",
            "status",
            "total_price",
            "discount_price",
            "items",
            "store",
            "products",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_products(self, obj):
        products = [item.store_item.product for item in obj.items.all()]
        serializer = ProductReadSerializer(products, many=True, context=self.context)
        return serializer.data

    def get_store(self, obj):
        store = [item.store_item.store for item in obj.items.all()]
        serializer = StoreItemReadSerializer(store)
        return serializer.data


class OrderWriteSerializer(serializers.ModelSerializer):
    address_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Order
        fields = ["address_id"]


class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["status"]
