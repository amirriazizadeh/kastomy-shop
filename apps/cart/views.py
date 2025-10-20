from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    CartSerializer,
)
from apps.cart.models import CartItem
from apps.stores.models import StoreItem
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


STORE_ITEM_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "id": openapi.Schema(type=openapi.TYPE_INTEGER, example=5),
        "name": openapi.Schema(type=openapi.TYPE_STRING, example="Product X"),
        "price": openapi.Schema(
            type=openapi.TYPE_NUMBER, format="float", example=99.99
        ),
    },
)

CART_ITEM_READ_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "id": openapi.Schema(type=openapi.TYPE_INTEGER, example=12),
        "store_item": STORE_ITEM_SCHEMA,
        "quantity": openapi.Schema(type=openapi.TYPE_INTEGER, example=2),
        "total_price": openapi.Schema(
            type=openapi.TYPE_NUMBER, format="float", example=199.98
        ),
    },
)

CART_READ_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "id": openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
        "user": openapi.Schema(type=openapi.TYPE_INTEGER, example=101),
        "items": openapi.Schema(type=openapi.TYPE_ARRAY, items=CART_ITEM_READ_SCHEMA),
        "total_amount": openapi.Schema(
            type=openapi.TYPE_NUMBER, format="float", example=350.50
        ),
        "total_items": openapi.Schema(type=openapi.TYPE_INTEGER, example=5),
    },
)

CART_ITEM_WRITE_REQUEST = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "quantity": openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
    },
    required=["quantity"],
)

MESSAGE_RESPONSE_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "message": openapi.Schema(
            type=openapi.TYPE_STRING, example="Cart item not found"
        ),
    },
)


class UserCart(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="My Cart",
        operation_description="see your cart",
        responses={
            200: openapi.Response(
                description="User cart details retrieved successfully",
                schema=CART_READ_SCHEMA,
            ),
        },
    )
    def get(self, request):
        user_cart = request.user.cart
        serializer = CartSerializer(user_cart, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

