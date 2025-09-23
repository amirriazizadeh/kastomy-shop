

from django.db import transaction, IntegrityError
from rest_framework import generics, permissions,status
from .models import Order,OrderItem
from .serializers import OrderSerializer,CheckoutSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from cart.models import Cart
import requests
import json
from django.conf import settings
from django.db import transaction
from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from .models import Order

class OrdersView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items', 'items__store_item')


class CheckoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, *args, **kwargs):
        try:
            cart = Cart.objects.get(user=request.user, is_active=True)
            if not cart.items.exists():
                return Response({"error": "سبد خرید شما خالی است."}, status=status.HTTP_400_BAD_REQUEST)
        except Cart.DoesNotExist:
            return Response({"error": "سبد خرید فعالی یافت نشد."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CheckoutSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        selected_address = validated_data.get('shipping_address')
        description_note = validated_data.get('description', None)

        try:
            with transaction.atomic():
                order = Order.objects.create(
                    user=request.user,
                    shipping_address=selected_address,
                    total_price=cart.total_price,
                    final_price=cart.total_price, 
                    discount_amount=0,
                    description=description_note,
                )

                for cart_item in cart.items.all():
                    store_item = cart_item.store_item
                    
                    if store_item.stock_quantity < cart_item.quantity:
                        raise IntegrityError(f"موجودی محصول {store_item} کافی نیست.")

                    OrderItem.objects.create(
                        order=order,
                        store_item=store_item,
                        quantity=cart_item.quantity,
                        price=cart_item.price
                    )
                    
                    store_item.stock_quantity -= cart_item.quantity
                    store_item.save(update_fields=['stock_quantity'])

                cart.is_active = False
                cart.save(update_fields=['is_active'])

        except IntegrityError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        order_result_serializer = OrderSerializer(order) 
        return Response({"payment_url":f"http://127.0.0.1:8000/api/payments/{order.id}/start/"}, status=status.HTTP_201_CREATED)
    

















ZP_API_REQUEST = "https://sandbox.zarinpal.com/pg/v4/payment/request.json"
ZP_API_STARTPAY = "https://sandbox.zarinpal.com/pg/StartPay/"
ZP_API_VERIFY = "https://sandbox.zarinpal.com/pg/v4/payment/verify.json"
CALLBACK_URL = "http://127.0.0.1:8000/api/payments/verify/"  


class PaymentRequestAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request,order_id ,*args, **kwargs):
        global order
        try:
            order = Order.objects.get(id=order_id, user=request.user, is_paid=False)
        except Order.DoesNotExist:
            return Response({"error": "سفارش معتبر یافت نشد یا قبلاً پرداخت شده است."},
                            status=status.HTTP_404_NOT_FOUND)
        price = int(order.final_price)*1000
        data = {
            "merchant_id": settings.MERCHANT,
            "amount": price,
            "description": f"پرداخت سفارش شماره {order.id}",
            "callback_url": CALLBACK_URL,
            "metadata": {"mobile": "09184222500", "email": "ariazizade@gmail.com"}
        }
        data = json.dumps(data)
        headers = {'content-type': 'application/json', 'content-length': str(len(data))}
        response = requests.post(ZP_API_REQUEST, data=data, headers=headers)
        if response.status_code == 200:
            response = response.json()
            if response["data"]['code'] == 100:
                url = f"{ZP_API_STARTPAY}{response['data']['authority']}"
                return redirect(url)
            else:
                return HttpResponse(str(response['errors']))
        else:
            return HttpResponse("مشکلی پیش آمد.")






class VerifyPaymentAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        status_param = request.GET.get('Status')
        authority = request.GET.get('Authority')
        if status_param != "OK":
            return HttpResponse("پرداخت شما ناموفق بود.", status=400)
        try:
            order = Order.objects.get(payment_authority=authority, user=request.user, is_paid=False)
        except Order.DoesNotExist:
            return HttpResponse("سفارش معتبر یافت نشد یا قبلاً پرداخت شده است.", status=404)
        data = {
            "merchant_id": settings.MERCHANT,
            "amount": int(order.final_price), 
            "authority": authority
            }
        headers = {'content-type': 'application/json', 'Accept': 'application/json'}
        response = requests.post(ZP_API_VERIFY, data=json.dumps(data), headers=headers)
        if response.status_code != 200:
            return HttpResponse("خطا در ارتباط با زرین‌پال.", status=500)
        res = response.json()
        code = res['data']['code']
        if code == 100:  
            with transaction.atomic():
                order.is_paid = True
                order.status = Order.OrderStatus.PAIED
                order.payment_reference = res['data']['ref_id']
                order.save(update_fields=['is_paid', 'status', 'payment_reference'])
                from cart.models import Cart
                Cart.objects.filter(user=request.user, is_active=False).delete()
            return HttpResponse(f"پرداخت موفق بود. کد پیگیری: {order.payment_reference}")
        elif code == 101:  
            return HttpResponse("این پرداخت قبلاً تأیید شده بود.")
        else:
            return HttpResponse("پرداخت شما ناموفق بود.", status=400)


















# //////////////////////////////////////////////////////////////////////////////////////////






















# views.py
import json
import requests
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect, render

if settings.SANDBOX:
    sandbox = 'sandbox'
else:
    sandbox = 'payment'

ZP_API_REQUEST = f"https://{sandbox}.zarinpal.com/pg/v4/payment/request.json"
ZP_API_STARTPAY = f"https://{sandbox}.zarinpal.com/pg/StartPay/"
ZP_API_VERIFY = f"https://{sandbox}.zarinpal.com/pg/v4/payment/verify.json"

description = "نهایی کردن خرید شما از سایت ما" # it's only an example

price = 100000 # it's only an example
CallbackURL = 'http://localhost:8000/api/payments/verify/' # you should customize it





def request_payment(request):
    data = {
        "merchant_id": settings.MERCHANT,
        "amount": price,
        "description": description,
        "callback_url": CallbackURL,
    }
    data = json.dumps(data)

    headers = {'content-type': 'application/json', 'content-length': str(len(data))}

    response = requests.post(ZP_API_REQUEST, data=data, headers=headers)

    if response.status_code == 200:
        response = response.json()

        if response["data"]['code'] == 100:
            url = f"{ZP_API_STARTPAY}{response['data']['authority']}"
            return redirect(url)

        else:
            return HttpResponse(str(response['errors']))

    else:
        return HttpResponse("مشکلی پیش آمد.")
    



def verify(request):
    status = request.GET.get('Status')
    authority = request.GET['Authority']

    if status == "OK":
        data = {
            "merchant_id": settings.MERCHANT,
            "amount": price,
            "authority": authority
        }
        data = json.dumps(data)

        headers = {'content-type': 'application/json', 'Accept': 'application/json'}

        response = requests.post(ZP_API_VERIFY, data=data, headers=headers)

        if response.status_code == 200:
            response = response.json()
            if response['data']['code'] == 100:
                # put your logic here
                return HttpResponse("خرید شما با موفقیت انجام شد.")

            elif response['data']['code'] == 101:
                return HttpResponse("این پرداخت قبلا انجام شده است.")

            else:
                return HttpResponse("پرداخت شما ناموفق بود.")

        else:
            return HttpResponse("پرداخت شما ناموفق بود.")

    else:
        return HttpResponse("پرداخت شما ناموفق بود.")





















