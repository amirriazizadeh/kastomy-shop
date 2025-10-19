

from django.db import transaction, IntegrityError
from django.urls import reverse
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
    













import requests
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect

MERCHANT = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
ZP_API_REQUEST = "https://sandbox.zarinpal.com/pg/v4/payment/request.json"
ZP_API_VERIFY = "https://sandbox.zarinpal.com/pg/v4/payment/verify.json"
ZP_API_STARTPAY = "https://sandbox.zarinpal.com/pg/StartPay/"

CALLBACK_URL = "http://127.0.0.1:8000/api/payments/verify/"  

def payment_request(request,order_id):
    global order
    try:
        order = Order.objects.get(id=order_id, user=request.user, is_paid=False)
    except Order.DoesNotExist:
            return JsonResponse("not define this order")
    amount = int(order.final_price)
    description = "خرید تستی"
    data = {
        "merchant_id": MERCHANT,
        "amount": amount,
        "callback_url": CALLBACK_URL,
        "description": description,
    }
    headers = {"accept": "application/json", "content-type": "application/json"}
    
    res = requests.post(ZP_API_REQUEST, json=data, headers=headers)
    if res.status_code == 200:
        res_json = res.json()
        if res_json["data"]["code"] == 100:
            authority = res_json["data"]["authority"]
            order.payment_authority=authority
            return redirect(ZP_API_STARTPAY + authority)
        else:
            return JsonResponse({"error": res_json["errors"]})
    else:
        return JsonResponse({"error": "خطا در ارتباط با زرین‌پال"})


def payment_verify(request):
    
    authority = request.GET.get("Authority")
    status = request.GET.get("Status")
    amount=int(order.final_price)
    if status == "OK":
        data = {
            "merchant_id": MERCHANT,
            "amount": amount,
            "authority": authority,
        }
        headers = {"accept": "application/json", "content-type": "application/json"}
        res = requests.post(ZP_API_VERIFY, json=data, headers=headers)
        if res.status_code == 200:
            res_json = res.json()
            if res_json["data"]["code"] == 100:
                with transaction.atomic():
                    order.is_paid = True
                    order.status = Order.OrderStatus.PAIED
                    order.payment_reference = str(res_json["data"]["ref_id"])
                    order.payment_authority = str(authority)
                    order.save(update_fields=['is_paid', 'status', 'payment_reference','payment_authority'])
                from cart.models import Cart
                Cart.objects.filter(user=request.user, is_active=False).delete()
                return JsonResponse({"status": "success", "ref_id": res_json["data"]["ref_id"]})
            else:
                return JsonResponse({"status": "failed", "code": res_json["data"]["code"]})
        else:
            return JsonResponse({"error": "ERROR in payment...."})
    else:
        return JsonResponse({"status": "canceled"})



























