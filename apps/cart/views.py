from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    CartItemReadSerializer,
    CartItemWriteSerializer,
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


class UserCartItem(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="My Cart Items",
        operation_description="see your cart items",
        responses={
            200: openapi.Response(
                description="List of cart items",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY, items=CART_ITEM_READ_SCHEMA
                ),
            ),
        },
    )
    def get(self, request):
        user_cart = request.user.cart
        cart_items = user_cart.items.all()
        serializer = CartItemReadSerializer(
            cart_items,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class CartItemDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            return CartItem.objects.get(pk=pk, cart=user.cart)
        except CartItem.DoesNotExist:
            return None

    @swagger_auto_schema(
        request_body=CART_ITEM_WRITE_REQUEST,
        operation_summary="Update Cart Item",
        operation_description="update a cart item by its pk (setting a new quantity)",
        responses={
            200: openapi.Response(
                description="Cart item updated successfully",
                schema=CART_ITEM_READ_SCHEMA,
            ),
            204: openapi.Response(
                description="Cart item quantity set to 0 and item deleted",
                schema=MESSAGE_RESPONSE_SCHEMA,
            ),
            404: openapi.Response(
                description="Cart item not found", schema=MESSAGE_RESPONSE_SCHEMA
            ),
            400: openapi.Response(
                description="Bad Request / Not enough stock",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="Not enough stock available",
                        )
                    },
                ),
            ),
        },
    )
    def patch(self, request, pk):
        cart_item = self.get_object(pk, request.user)
        if not cart_item:
            return Response(
                {"message": "Cart item not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = CartItemWriteSerializer(
            instance=cart_item,
            data=request.data,
            partial=True,
            context={
                "request": request,
                "store_item": cart_item.store_item,
            },
        )

        if serializer.is_valid():
            new_quantity = serializer.validated_data.get("quantity")  # type: ignore
            if new_quantity is not None:
                if new_quantity <= 0:  # type: ignore
                    cart_item.delete()
                    return Response(
                        {"message": "Cart item deleted"},
                        status=status.HTTP_204_NO_CONTENT,
                    )
                store_item = cart_item.store_item
                if new_quantity > store_item.stock:  # type: ignore
                    return Response(
                        {"message": "Not enough stock available"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            serializer.save()
            response_serializer = CartItemReadSerializer(
                cart_item,
                context={"request": request},
            )
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Delete Cart Item",
        operation_description="delete a cart item by its pk",
        responses={
            204: openapi.Response(
                description="Cart item deleted successfully (No Content)",
            ),
            404: openapi.Response(
                description="Cart item not found", schema=MESSAGE_RESPONSE_SCHEMA
            ),
        },
    )
    def delete(self, request, pk):
        cart_item = self.get_object(pk, request.user)
        if not cart_item:
            return Response(
                {"message": "Cart item not found"}, status=status.HTTP_404_NOT_FOUND
            )
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AddStoreItemToCart(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=CartItemWriteSerializer,
        operation_summary="Add Store Item To Cart",
        operation_description="add a store item to your cart by its pk (URL path parameter)",
        responses={
            201: openapi.Response(
                description="Item added to cart (new item)",
                schema=CART_ITEM_READ_SCHEMA,
            ),
            200: openapi.Response(
                description="Item quantity updated (existing item)",
                schema=CART_ITEM_READ_SCHEMA,
            ),
            404: openapi.Response(
                description="Store item not found", schema=MESSAGE_RESPONSE_SCHEMA
            ),
            400: openapi.Response(
                description="Bad Request / Not enough stock",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="Not enough stock available",
                        )
                    },
                ),
            ),
        },
    )
    def post(self, request, pk):
        try:
            store_item = StoreItem.objects.get(pk=pk, is_active=True)
        except StoreItem.DoesNotExist:
            return Response(
                {"message": "Store item not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        user_cart = request.user.cart

        serializer = CartItemWriteSerializer(
            data=request.data, context={"request": request, "store_item": store_item}
        )

        if serializer.is_valid():
            quantity_to_add = serializer.validated_data.get("quantity", 1)  # type: ignore
            cart_item, created = CartItem.objects.get_or_create(
                cart=user_cart, store_item=store_item, defaults={"quantity": 0}
            )
            if cart_item.quantity + quantity_to_add > store_item.stock:
                return Response(
                    {"message": "Not enough stock available"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            cart_item.quantity += quantity_to_add
            cart_item.save()
            response_serializer = CartItemReadSerializer(
                cart_item,
                context={"request": request},
            )
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
