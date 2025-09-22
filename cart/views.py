from django.utils import timezone
from decimal import Decimal
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from .models import Cart, CartItem, StoreItem
from .serializers import AddToCartSerializer, CartItemSerializer,CartSerializer
from orders.models import Discount,DiscountUsage

class CartView(APIView):
    """
    API endpoint to retrieve all items in the current user's cart.
    URL: /api/mycart/
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cart = Cart.objects.filter(
            user=request.user,
            is_active=True,
            expires_at__gt=timezone.now()
        ).first()
        if not cart:
            return Response({"message": "Your cart is empty."}, status=status.HTTP_200_OK)
        return Response(CartSerializer(cart).data)
    
    def post(self, request):
        code = request.data.get('code')
        if not code:  # اگر کدی وارد نشد
            return Response({"message": "No discount applied."}, status=status.HTTP_200_OK)

        # پیدا کردن کد تخفیف
        try:
            discount = Discount.objects.get(code=code, expire_at__gt=timezone.now())
        except Discount.DoesNotExist:
            return Response({"error": "کد تخفیف معتبر نیست یا منقضی شده."},
                            status=status.HTTP_400_BAD_REQUEST)

        # بررسی استفاده قبلی
        if DiscountUsage.objects.filter(discount=discount, user=request.user).exists():
            return Response({"error": "شما قبلاً از این کد تخفیف استفاده کرده‌اید."},
                            status=status.HTTP_400_BAD_REQUEST)

        # اعمال تخفیف روی مبلغ سبد
        cart = Cart.objects.filter(
            user=request.user,
            is_active=True,
            expires_at__gt=timezone.now()
        ).first()
        if not cart:
            return Response({"message": "Your cart is empty."}, status=status.HTTP_200_OK)

        cart.total_price = cart.total_price * (Decimal('1') - (Decimal(discount.percent) / Decimal('100')))
        cart.save()

        # ذخیره استفاده از تخفیف
        DiscountUsage.objects.create(discount=discount, user=request.user)

        return Response({"message": "تخفیف اعمال شد.", "total_price": cart.total_price},
                        status=status.HTTP_200_OK)
    # def post(self, request):
    #     """
    #     Optionally apply a discount code to the cart.
    #     Expects JSON: {"code": "DISCOUNT10"} or {} for no discount.
    #     """
    #     code = request.data.get('code', '').strip()
    #     cart = Cart.objects.filter(
    #         user=request.user,
    #         is_active=True,
    #         expires_at__gt=timezone.now()
    #     ).first()
    #     if not cart:
    #         return Response({"detail": "Cart not found."},
    #                         status=status.HTTP_404_NOT_FOUND)

    #     if not code:
    #         return Response({
    #             "message": "No discount applied.",
    #             "total_price": str(cart.total_price)
    #         })

    #     try:
    #         discount = Discount.objects.get(name=code)
    #     except Discount.DoesNotExist:
    #         return Response({"detail": "Discount code not found."},
    #                         status=status.HTTP_404_NOT_FOUND)

    #     if DiscountUsage.objects.filter(discount=discount, user=request.user).exists():
    #         return Response({"error": "شما قبلاً از این کد تخفیف استفاده کرده‌اید."},
    #                         status=status.HTTP_400_BAD_REQUEST)
    #     try:
    #         discount = Discount.objects.get(code=code, expire_at__gt=timezone.now())
    #     except Discount.DoesNotExist:
    #         return Response({"error": "کد تخفیف معتبر نیست یا منقضی شده."},
    #                         status=status.HTTP_400_BAD_REQUEST)


    #     original_total = cart.total_price
    #     discount_amount = (original_total * discount.percent) / 100
    #     discounted_total = original_total - discount_amount

    #     cart.total_price = discounted_total
    #     cart.save(update_fields=['total_price'])

    #     return Response({
    #         "message": f"Discount code applied: {discount.name}",
    #         "original_total": str(original_total),
    #         "discount_percent": str(discount.percent),
    #         "discounted_total": str(discounted_total)
    #     })

class CartDetailView(APIView):
    """
    API endpoint to retrieve all items in the current user's cart.
    URL: /api/mycart/
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, request, id):
        cart = Cart.objects.filter(
            user=request.user,
            is_active=True,
            expires_at__gt=timezone.now()
        ).first()
        if not cart:
            return None, Response({"detail": "Cart not found."}, status=status.HTTP_404_NOT_FOUND)
        item = get_object_or_404(CartItem, pk=id, cart=cart)
        return item, None

    def get(self, request, id):
        item, error = self.get_object(request, id)
        if error:
            return error
        return Response(CartItemSerializer(item).data)

    def patch(self, request, id):
        item, error = self.get_object(request, id)
        if error:
            return error

        # بررسی اینکه کاربر سعی نکرده فیلد read-only رو تغییر بده
        forbidden_fields = ['price', 'total_price']
        for field in forbidden_fields:
            if field in request.data:
                return Response(
                    {"detail": f"فیلد '{field}' قابل تغییر نیست. فقط تعداد قابل ویرایش است."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = CartItemSerializer(
            item, data=request.data, partial=True, context={'store_item': item.store_item}
        )
        if serializer.is_valid():
            serializer.save()
            item.cart.update_total()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        item, error = self.get_object(request, id)
        if error:
            return error
        cart = item.cart
        item.delete()
        cart.update_total()
        return Response({"message": "Item deleted."}, status=status.HTTP_204_NO_CONTENT)
        


class AddToCartView(APIView):
    """
    API endpoint to add a product to the user's cart.
    URL: /api/mycart/add_to_cart/<int:id>/
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, product_id):
        quantity = int(request.data.get('quantity', 1))
        store_item = get_object_or_404(StoreItem, pk=product_id, is_active=True)

        if store_item.stock_quantity < quantity:
            return Response({"detail": "موجودی کافی نیست."}, status=status.HTTP_400_BAD_REQUEST)

        # پیدا کردن یا ساخت سبد فعال
        cart, created = Cart.objects.get_or_create(
            user=request.user,
            is_active=True,
            expires_at__gt=timezone.now(),
            defaults={}
        )

        # بررسی آیتم قبلی
        cart_item = CartItem.objects.filter(cart=cart, store_item=store_item).first()
        if cart_item:
            cart_item.quantity += quantity
            cart_item.save()
        else:
            cart_item = CartItem.objects.create(
                cart=cart,
                store_item=store_item,
                quantity=quantity,
                price=store_item.price
            )

        # بروزرسانی قیمت کل
        cart.update_total()
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

