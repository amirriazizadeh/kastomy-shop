from decimal import Decimal
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from .models import Cart, CartItem, StoreItem
from .serializers import AddToCartSerializer, CartItemSerializer


class CartView(APIView):
    def get(self,request):
        return Response({"massage":"salam"})



class AddToCartView(APIView):
    """
    API endpoint to add a product to the user's cart.
    URL: /api/mycart/add_to_cart/<int:id>/
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        quantity = serializer.validated_data['quantity']

        store_item = get_object_or_404(StoreItem, pk=id)

        cart, created = Cart.objects.get_or_create(user=request.user)

        cart_item, item_created = CartItem.objects.get_or_create(
            cart=cart,
            store_item=store_item,
            defaults={'price': store_item.price, 'quantity': quantity}
        )

        if not item_created:
            # Update quantity if item exists
            cart_item.quantity += quantity
            cart_item.save()

        # Update total price for the cart
        cart.total_price = sum(item.total_price for item in cart.items.all())
        cart.save()

        # Serialize the updated/created item
        output_serializer = CartItemSerializer(cart_item)
        return Response({
            "message": "Product added to cart successfully.",
            "cart_id": cart.id,
            "total_price": str(cart.total_price),
            "item": output_serializer.data
        }, status=status.HTTP_200_OK)
