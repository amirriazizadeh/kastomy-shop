from rest_framework import serializers
from apps.payments.models import Payment
from apps.orders.serializers import OrderReadSerializer


class PaymentReadSerializer(serializers.ModelSerializer):
    order = OrderReadSerializer(read_only=True)
    payment_url = serializers.CharField(read_only=True)  

    class Meta:
        model = Payment
        fields = [
            "id",
            "order",
            "transaction_id",
            "amount",
            "gateway",
            "payment_url",  
        ]
        read_only_fields = fields
