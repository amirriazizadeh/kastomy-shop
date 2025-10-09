from django.utils import timezone
from decimal import Decimal
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Cart, CartItem, StoreItem
from .serializers import (AddToCartSerializer, CartItemSerializer,
                CartSerializer,AddToCartInputSerializer,ApplyDiscountInputSerializer)
from orders.models import Discount,DiscountUsage
from drf_spectacular.utils import extend_schema



class CartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="نمایش سبد خرید",
        description="این متد تمام آیتم‌های موجود در سبد خرید فعال کاربر را برمی‌گرداند.",
        responses={
            200: CartSerializer,
        }
    )
    def get(self, request):
        cart = Cart.objects.filter(user=request.user,is_active=True,expires_at__gt=timezone.now()).first()
        if not cart:
            return Response({"items":[],'total_price':00.00,'total_discount':00.00}, status=status.HTTP_200_OK)
        return Response(CartSerializer(cart).data)

    @extend_schema(
        summary="اعمال کد تخفیف",
        description="این متد یک کد تخفیف معتبر را روی سبد خرید کاربر اعمال می‌کند و مبلغ کل سبد را به‌روزرسانی می‌نماید.",
        request=ApplyDiscountInputSerializer,
        responses={
            200: dict,
            400: dict,
        }
    )
    def post(self, request):
        code = request.data.get('code')
        if not code:
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

        # پیدا کردن سبد خرید فعال
        cart = Cart.objects.filter(
            user=request.user,
            is_active=True,
            expires_at__gt=timezone.now()
        ).first()
        if not cart:
            return Response({"message": "Your cart is empty."}, status=status.HTTP_200_OK)

        # اعمال تخفیف
        cart.total_price = cart.total_price * (Decimal('1') - (Decimal(discount.percent) / Decimal('100')))
        cart.save()

        # ذخیره استفاده از تخفیف
        DiscountUsage.objects.create(discount=discount, user=request.user)

        return Response(
            {"message": "تخفیف اعمال شد.", "total_price": cart.total_price},
            status=status.HTTP_200_OK
        )






class CartDetailView(APIView):
    """
    مدیریت آیتم خاصی از سبد خرید کاربر.

    آدرس: 
        `/api/mycart/<int:id>/`

    توضیحات:
        - **GET**: دریافت اطلاعات یک آیتم خاص از سبد خرید.  
        - **PATCH**: ویرایش جزئی (مثلاً تعداد) یک آیتم.  
        - **DELETE**: حذف آیتم از سبد خرید.  
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, request, id):
        """دریافت آیتم سبد خرید متعلق به کاربر یا بازگرداندن خطا"""
        cart = Cart.objects.filter(
            user=request.user,
            is_active=True,
            expires_at__gt=timezone.now()
        ).first()
        if not cart:
            return None, Response({"detail": "Cart not found."}, status=status.HTTP_404_NOT_FOUND)
        item = get_object_or_404(CartItem, pk=id, cart=cart)
        return item, None

    @extend_schema(
        summary="دریافت آیتم سبد خرید",
        description="اطلاعات یک آیتم خاص از سبد خرید کاربر را برمی‌گرداند.",
        responses={200: CartItemSerializer, 404: dict}
    )
    def get(self, request, id):
        item, error = self.get_object(request, id)
        if error:
            return error
        return Response(CartItemSerializer(item).data)

    @extend_schema(
        summary="ویرایش آیتم سبد خرید",
        description="ویرایش بخشی از اطلاعات آیتم (مانند تعداد). فیلدهای فقط‌خواندنی مثل `price` و `total_price` قابل تغییر نیستند.",
        request=CartItemSerializer,
        responses={200: CartItemSerializer, 400: dict, 404: dict}
    )
    def patch(self, request, id):
        item, error = self.get_object(request, id)
        if error:
            return error

        # جلوگیری از تغییر فیلدهای فقط‌خواندنی
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

    @extend_schema(
        summary="حذف آیتم از سبد خرید",
        description="این متد یک آیتم مشخص از سبد خرید کاربر را حذف می‌کند.",
        responses={204: dict, 404: dict}
    )
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
    افزودن یک محصول به سبد خرید کاربر.

    آدرس:
        `/api/mycart/add_to_cart/<int:product_id>/`

    توضیحات:
        - فقط کاربران لاگین کرده می‌توانند محصولی به سبد خرید اضافه کنند.
        - اگر محصول از قبل در سبد وجود داشته باشد، تعداد آن افزایش می‌یابد.
        - در نهایت اطلاعات کامل سبد خرید برگردانده می‌شود.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="افزودن محصول به سبد خرید",
        description=(
            "این متد یک محصول مشخص را با تعداد دلخواه به سبد فعال کاربر اضافه می‌کند. "
            "اگر محصول قبلاً در سبد باشد، تعداد آن افزایش داده می‌شود."
        ),
        request=AddToCartInputSerializer,
        responses={
            200: CartSerializer,
            400: dict,
            404: dict,
        }
    )
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











# class AddToCartView(APIView):
#     """
#     API endpoint to add a product to the user's cart.
#     URL: /api/mycart/add_to_cart/<int:id>/
#     """
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request, product_id):
#         quantity = int(request.data.get('quantity', 1))
#         store_item = get_object_or_404(StoreItem, pk=product_id, is_active=True)

#         if store_item.stock_quantity < quantity:
#             return Response({"detail": "موجودی کافی نیست."}, status=status.HTTP_400_BAD_REQUEST)

#         # پیدا کردن یا ساخت سبد فعال
#         cart, created = Cart.objects.get_or_create(
#             user=request.user,
#             is_active=True,
#             expires_at__gt=timezone.now(),
#             defaults={}
#         )

#         # بررسی آیتم قبلی
#         cart_item = CartItem.objects.filter(cart=cart, store_item=store_item).first()
#         if cart_item:
#             cart_item.quantity += quantity
#             cart_item.save()
#         else:
#             cart_item = CartItem.objects.create(
#                 cart=cart,
#                 store_item=store_item,
#                 quantity=quantity,
#                 price=store_item.price
#             )

#         # بروزرسانی قیمت کل
#         cart.update_total()
#         return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

