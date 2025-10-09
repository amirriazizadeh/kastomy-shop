from rest_framework import serializers
from .models import CartItem,Cart


class CartItemSerializer(serializers.ModelSerializer):
    store_item_name = serializers.CharField(
        source='store_item.variant.product.name', read_only=True
    )

    class Meta:
        model = CartItem
        fields = ['id', 'store_item_name', 'quantity', 'price', 'total_price']
        read_only_fields = ['id', 'store_item_name', 'price', 'total_price']

    def validate(self, attrs):
        if 'price' in self.initial_data or 'total_price' in self.initial_data:
            raise serializers.ValidationError(
                "این آیتم قابل تغییر نیست. فقط تعداد قابل ویرایش است."
            )
        return super().validate(attrs)

    def validate_quantity(self, value):
        store_item = self.instance.store_item if self.instance else self.context.get('store_item')
        if value > store_item.stock_quantity:
            raise serializers.ValidationError("موجودی کافی نیست.")
        if value < 1:
            raise serializers.ValidationError("تعداد باید حداقل ۱ باشد.")
        return value

    def update(self, instance, validated_data):
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.price = instance.store_item.price
        instance.save()
        return instance



class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['items', 'total_price', 'total_discount']




class AddToCartSerializer(serializers.Serializer):
    """Validate quantity for adding to cart."""
    quantity = serializers.IntegerField(min_value=1)
    def validate(self, attrs):
        request = self.context.get('request')
        store_item = self.context.get('store_item') 
        quantity = attrs.get('quantity')

        # Check stock availability
        if store_item.stock_quantity < quantity:
            raise serializers.ValidationError(
                {"quantity": f"Only {store_item.stock_quantity} items are available in stock."}
            )
        return attrs

class CartItemSerializer(serializers.ModelSerializer):
    """Serialize cart item details."""
    store_item_name = serializers.CharField(source='store_item.variant.product.name', read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'store_item_name', 'quantity', 'price', 'total_price']
        read_only_fields = ['price', 'total_price']

class AddToCartInputSerializer(serializers.Serializer):
    """ورودی برای افزودن محصول به سبد خرید"""
    quantity = serializers.IntegerField(
        required=False, default=1, min_value=1,
        help_text="تعداد محصولی که باید به سبد اضافه شود (پیش‌فرض = 1)."
    )

class ApplyDiscountInputSerializer(serializers.Serializer):
    """ورودی برای اعمال کد تخفیف روی سبد خرید"""
    code = serializers.CharField(
        required=True,
        help_text="کد تخفیف معتبر که باید روی سبد خرید اعمال شود."
    )