

from rest_framework import serializers
from .models import Order, OrderItem
from accounts.models import Address




class CheckoutSerializer(serializers.Serializer):
    """
    سریالایزری برای دریافت آدرس در فرآیند checkout.
    این سریالایزر به صورت داینامیک آدرس‌های کاربر فعلی را نمایش می‌دهد.
    """
    shipping_address = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.none(),
        label="آدرس ارسال"
    )

    def __init__(self, *args, **kwargs):
        """
        با بازنویسی این متد، کوئری‌ست فیلد آدرس را بر اساس کاربر
        موجود در context فیلتر می‌کنیم.
        """
        # اول متد اصلی را اجرا می‌کنیم
        super().__init__(*args, **kwargs)

        # از context که در ویو پاس داده شده، request را استخراج می‌کنیم
        request = self.context.get('request', None)
        if request and hasattr(request, "user"):
            user = request.user
            # کوئری‌ست فیلد آدرس را به آدرس‌های کاربر فعلی محدود می‌کنیم
            self.fields['shipping_address'].queryset = Address.objects.filter(user=user)

# سریالایزرهای زیر برای نمایش خروجی نهایی هستند
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['store_item', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    address = serializers.StringRelatedField() # نمایش متنی آدرس

    class Meta:
        model = Order
        fields = ['id', 'user', 'address', 'total_price', 'is_paid', 'created_at', 'items']



