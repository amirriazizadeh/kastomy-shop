from rest_framework import serializers
from .models import CartItem

class AddToCartSerializer(serializers.Serializer):
    """Validate quantity for adding to cart."""
    quantity = serializers.IntegerField(min_value=1)

class CartItemSerializer(serializers.ModelSerializer):
    """Serialize cart item details."""
    store_item_name = serializers.CharField(source='store_item.variant.product.name', read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'store_item_name', 'quantity', 'price', 'total_price']
