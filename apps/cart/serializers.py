from rest_framework import serializers
from apps.cart.models import Cart, CartItem
from apps.users.serializers_base import UserSimpleSerializer
from apps.products.serializers import ProductReadSerializer
from apps.stores.serializers import StoreItemReadSerializer




class CartItemReadSerializer(serializers.ModelSerializer):
    store_item = StoreItemReadSerializer(read_only=True)
    total_price = serializers.SerializerMethodField()
    store = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()
    price = serializers.DecimalField(
        source="store_item.price", max_digits=12, decimal_places=2, read_only=True
    )
    discount_price = serializers.DecimalField(
        source="store_item.total_price",
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )
    discount_amount = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            "id",
            "store_item",
            "store",
            "product",
            "price",
            "discount_price",
            "quantity",
            "added_at",
            "total_price",
            "discount_amount",
        ]
        read_only_fields = fields

    def get_total_price(self, obj):
        return obj.quantity * obj.store_item.total_price

    def get_store(self, obj):
        return {
            "id": obj.store_item.store.id if obj.store_item.store else None,
            "name": obj.store_item.store.name if obj.store_item.store else None,
        }

    def get_product(self, obj):
        serializer = ProductReadSerializer(obj.store_item.product, context=self.context)
        return serializer.data

    def get_discount_amount(self, obj):
        return obj.store_item.discount or 0






class CartSerializer(serializers.ModelSerializer):
    user = UserSimpleSerializer(read_only=True)
    items = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    total_discount = serializers.SerializerMethodField()
    products = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["user", "items", "total_price", "total_discount", "products"]

    def get_items(self, obj):
        items = obj.items.all()
        return CartItemReadSerializer(items, many=True, context=self.context).data

    def get_total_price(self, obj):
        total = sum(
            item.quantity * item.store_item.total_price for item in obj.items.all()
        )
        return total

    def get_total_discount(self, obj):
        total_discount = sum(
            item.quantity * (item.store_item.price - item.store_item.total_price)
            for item in obj.items.all()
        )
        return total_discount

    def get_products(self, obj):
        products = [item.store_item.product for item in obj.items.all()]
        serializer = ProductReadSerializer(products, many=True, context=self.context)
        return serializer.data
