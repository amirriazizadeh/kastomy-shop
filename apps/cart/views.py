from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem
from apps.stores.models import StoreItem
from .serializers import CartSerializer, CartItemSerializer


class MyCartView(APIView):
    """
    /api/mycart/
    دریافت سبد خرید فعال کاربر
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user, is_active=True)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MyCartItemsView(generics.ListAPIView):
    """
    /api/mycart/items/
    لیست تمام آیتم‌های سبد خرید فعال کاربر
    """
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None 

    def get_queryset(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user, is_active=True)
        return cart.items.select_related("store_item__store", "store_item__product")



class AddToCartView(APIView):
    """
    /api/mycart/add_to_cart/<store_item_id>/
    افزودن یک محصول به سبد خرید
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        quantity = int(request.data.get("quantity", 1))
        store_item = get_object_or_404(StoreItem, id=id)

        cart, _ = Cart.objects.get_or_create(user=request.user, is_active=True)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            store_item=store_item,
            defaults={"quantity": quantity},
        )

        if not created:
            cart_item.quantity += quantity

        cart_item.save()
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CartItemDetailView(APIView):
    """
    /api/mycart/items/<id>/
    مشاهده، ویرایش یا حذف آیتم خاص از سبد خرید
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, request, id):
        return get_object_or_404(
            CartItem, id=id, cart__user=request.user, cart__is_active=True
        )

    def get(self, request, id):
        item = self.get_object(request, id)
        serializer = CartItemSerializer(item)
        return Response(serializer.data)

    def patch(self, request, id):
        item = self.get_object(request, id)
        quantity = request.data.get("quantity")
        if quantity is not None:
            item.quantity = int(quantity)
            item.save()
        serializer = CartItemSerializer(item)
        return Response(serializer.data)

    def delete(self, request, id):
        item = self.get_object(request, id)
        cart = item.cart
        item.delete()
        cart.update_total()
        return Response(status=status.HTTP_204_NO_CONTENT)
