from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from apps.payments.models import Payment
from .serializers import PaymentReadSerializer
from django.conf import settings
import requests
from .tasks import send_payment_success_email
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import transaction
from apps.orders.models import Order


PAYMENT_READ_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "id": openapi.Schema(type=openapi.TYPE_INTEGER, example=15),
        "order": openapi.Schema(type=openapi.TYPE_INTEGER, example=10),
        "amount": openapi.Schema(
            type=openapi.TYPE_NUMBER, format="float", example=150.75
        ),
        "status": openapi.Schema(
            type=openapi.TYPE_STRING,
            enum=["PENDING", "PROGRESS", "VERIFIED", "FAILED"],
            example="PROGRESS",
        ),
        "transaction_id": openapi.Schema(
            type=openapi.TYPE_STRING, example="A0000000000000000000000000000010"
        ),
        "ref_id": openapi.Schema(type=openapi.TYPE_STRING, example="123456789"),
        "created_at": openapi.Schema(
            type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME
        ),
    },
)

START_PAYMENT_RESPONSE = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "url": openapi.Schema(
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_URI,
            example="https://www.zarinpal.com/pg/StartPay/A0000000000000000000000000000010",
        ),
    },
    required=["url"],
)

ERROR_RESPONSE_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "error": openapi.Schema(type=openapi.TYPE_STRING, example="Payment not found"),
    },
)

MESSAGE_RESPONSE_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "message": openapi.Schema(
            type=openapi.TYPE_STRING,
            example="Payment received, verification in progress. Check back soon.",
        ),
    },
)


class PaymentList(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="All My Payments",
        operation_description="see all of your payments",
        responses={
            200: openapi.Response(
                description="List of user's payments",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY, items=PAYMENT_READ_SCHEMA
                ),
            ),
        },
    )
    def get(self, request):
        payments = Payment.objects.filter(order__customer=request.user)
        serializer = PaymentReadSerializer(payments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ZarinPalResultPayment(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        authority = request.GET.get("Authority")
        status_param = request.GET.get("Status")
        FRONTEND_URL = "http://localhost:8080/profile/orders"

        try:
            payment = Payment.objects.get(transaction_id=authority)
        except Payment.DoesNotExist:
            return HttpResponse("<h1>Payment not found</h1>", status=404)

        if status_param == "OK":
            payload = {
                "merchant_id": settings.ZARINPAL_MERCHANT_ID,
                "authority": payment.transaction_id,
                "amount": int(payment.amount * 10),
            }
            try:
                res = requests.post(
                    settings.ZARINPAL_VERIFY_URL,
                    json=payload,
                    timeout=int(settings.OTP_TIME),
                )
                res.raise_for_status()
                res_json = res.json()

                if res_json.get("data", {}).get("code") in [100, 101]:
                    with transaction.atomic():
                        payment.status = Payment.PaymentStatus.DONE
                        payment.order.status = Order.OrderStatus.PROCESSING
                        payment.save()
                        payment.order.save()
                        user_cart = payment.order.customer.cart
                        user_cart.items.all().delete()
                    send_payment_success_email.delay(
                        payment.order.customer.email, payment.order.pk
                    )
                    message = "Payment successful. Verification complete."
                else:
                    with transaction.atomic():
                        payment.status = Payment.PaymentStatus.FAILED
                        payment.order.status = Order.OrderStatus.FAILED
                        payment.save()
                        payment.order.save()
                    message = "Payment failed during verification."
            except Exception as e:
                message = f"Error verifying payment: {e}"

        else:
            with transaction.atomic():
                payment.status = Payment.PaymentStatus.FAILED
                payment.order.status = Order.OrderStatus.FAILED
                payment.save()
                payment.order.save()
            message = "Payment cancelled or failed."

        html = f"""
        <html>
            <head><meta http-equiv="refresh" content="5;url={FRONTEND_URL}" /></head>
            <body><h2>{message}</h2></body>
        </html>
        """
        return HttpResponse(html)
