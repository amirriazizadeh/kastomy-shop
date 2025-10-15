from rest_framework import serializers
from .models import CartItem,Cart
from products.serializers import ProductSerializer

from products.models import Product
from stores.models import Store,StoreItem



class StoreInCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        exclude = ['address']

class StoreItemInCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreItem
        fields = ['id', 'price', 'discount_price', 'stock', 'store']

class CartItemSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    store = serializers.SerializerMethodField()
    store_item = StoreItemInCartSerializer(read_only=True)
    
    class Meta:
        model = CartItem
        fields = [
            'id', 'product', 'quantity', 'store', 
            'total_item_price', 'total_discount', 
            'total_price', 'unit_price', 'store_item'
        ]
    
    def get_product(self, obj):
        return ProductSerializer(obj.store_item.product).data
    
    def get_store(self, obj):
        return StoreInCartSerializer(obj.store_item.store).data



class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Cart
        fields = ['items', 'total_price', 'total_discount']
    
    def to_representation(self, instance):
        """اطمینان از اینکه همیشه items وجود داره"""
        data = super().to_representation(instance)
        if data.get('items') is None:
            data['items'] = []
        return data




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