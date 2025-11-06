from random import randint
import requests
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from .serializers import OrderReadSerializer, OrderWriteSerializer
from apps.orders.models import Order, OrderItem
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from apps.addresses.models import Address
from django.db import transaction
from django.conf import settings
import json
from apps.payments.models import Payment
from apps.payments.serializers import PaymentReadSerializer

ORDER_ITEM_READ_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "id": openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
        "store_item": openapi.Schema(type=openapi.TYPE_INTEGER, example=5),
        "quantity": openapi.Schema(type=openapi.TYPE_INTEGER, example=2),
        "price": openapi.Schema(
            type=openapi.TYPE_NUMBER, format="float", example=10.00
        ),
        "total_price": openapi.Schema(
            type=openapi.TYPE_NUMBER, format="float", example=20.00
        ),
    },
)

ORDER_READ_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "id": openapi.Schema(type=openapi.TYPE_INTEGER, example=10),
        "customer": openapi.Schema(type=openapi.TYPE_INTEGER, example=101),
        "address": openapi.Schema(type=openapi.TYPE_INTEGER, example=20),
        "total_price": openapi.Schema(
            type=openapi.TYPE_NUMBER, format="float", example=150.75
        ),
        "status": openapi.Schema(
            type=openapi.TYPE_STRING,
            enum=["PENDING", "PROCESSING", "SHIPPED", "DELIVERED", "CANCELLED"],
            example="PENDING",
        ),
        "created_at": openapi.Schema(
            type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME
        ),
        "items": openapi.Schema(type=openapi.TYPE_ARRAY, items=ORDER_ITEM_READ_SCHEMA),
    },
)

ORDER_WRITE_REQUEST = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "address_id": openapi.Schema(
            type=openapi.TYPE_INTEGER,
            example=20,
            description="ID of the user's selected address for delivery.",
        ),
    },
    required=["address_id"],
)

CREATE_ORDER_RESPONSE_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "id": openapi.Schema(type=openapi.TYPE_INTEGER, example=15),
        "order": ORDER_READ_SCHEMA,
        "transaction_id": openapi.Schema(type=openapi.TYPE_STRING, example="123456"),
        "amount": openapi.Schema(type=openapi.TYPE_NUMBER, example=150.75),
        "gateway": openapi.Schema(type=openapi.TYPE_STRING, example="ZarinPal"),
        "status": openapi.Schema(type=openapi.TYPE_STRING, example="PROGRESS"),
        "payment_url": openapi.Schema(
            type=openapi.TYPE_STRING,
            example="https://www.zarinpal.com/pg/StartPay/123456",
        ),
    },
)


MESSAGE_RESPONSE_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "message": openapi.Schema(
            type=openapi.TYPE_STRING, example="Error message here."
        ),
    },
)

PAGINATED_ORDER_RESPONSE = openapi.Response(
    description="Paginated list of user orders",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "count": openapi.Schema(type=openapi.TYPE_INTEGER, example=5),
            "next": openapi.Schema(
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_URI,
                example="http://api.example.com/orders?page=2",
            ),
            "previous": openapi.Schema(
                type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, example=None
            ),
            "results": openapi.Schema(type=openapi.TYPE_ARRAY, items=ORDER_READ_SCHEMA),
        },
    ),
)


class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="All Orders",
        operation_description="all orders in list form. Filterable by 'status' query param.",
        responses={
            200: PAGINATED_ORDER_RESPONSE,
        },
        manual_parameters=[
            openapi.Parameter(
                "status",
                openapi.IN_QUERY,
                description="Filter orders by status (e.g., PENDING, SHIPPED)",
                type=openapi.TYPE_STRING,
                enum=["PENDING", "PROCESSING", "SHIPPED", "DELIVERED", "CANCELLED"],
            ),
            openapi.Parameter(
                "page_size",
                openapi.IN_QUERY,
                description="Number of results per page (default: 5)",
                type=openapi.TYPE_INTEGER,
            ),
        ],
    )
    def get(self, request):
        orders = Order.objects.filter(customer=request.user).order_by("-id")
        search_term = request.query_params.get("status", "")
        if search_term:
            try:
                status_value = Order.OrderStatus[search_term.upper()].value
                orders = orders.filter(status=status_value).distinct()
            except Exception:
                orders = orders.none()
        paginator = PageNumberPagination()
        try:
            page_size = int(request.query_params.get("page_size", 5))  # type: ignore
        except ValueError:
            page_size = 5

        paginator.page_size = page_size
        result_page = paginator.paginate_queryset(orders, request)
        data = OrderReadSerializer(
            result_page, many=True, context={"request": request}
        ).data
        return paginator.get_paginated_response(data)


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="An Order",
        operation_description="an order detail's by its primary key (pk)",
        responses={
            200: openapi.Response(
                description="Order details retrieved successfully",
                schema=ORDER_READ_SCHEMA,
            ),
            400: openapi.Response(
                description="Order not found for the user",
                schema=MESSAGE_RESPONSE_SCHEMA,
            ),
        },
    )
    def get(self, request, pk):
        try:
            order = Order.objects.get(pk=pk, customer=request.user)
        except Order.DoesNotExist:
            return Response(
                {"message": "no such order for you"}, status=status.HTTP_400_BAD_REQUEST
            )
        serializer = OrderReadSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Delete An Order (Cancel)",
        operation_description="Cancel an order by its pk. Only pending orders can be cancelled.",
        responses={
            204: openapi.Response(
                description="Order cancelled successfully (No Content)",
            ),
            400: openapi.Response(
                description="Bad Request (e.g., trying to cancel a non-pending order)",
                schema=MESSAGE_RESPONSE_SCHEMA,
            ),
        },
    )
    def delete(self, request, pk):
        try:
            order = Order.objects.get(pk=pk, customer=request.user)
        except Order.DoesNotExist:
            return Response(
                {"message": "no such order"}, status=status.HTTP_400_BAD_REQUEST
            )
        if order.status != Order.OrderStatus.PENDING:
            return Response(
                {"message": "Only pending orders can be cancelled"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        with transaction.atomic():
            for item in order.items.all():  # type: ignore
                item.store_item.stock += item.quantity
                item.store_item.save()
            order.status = Order.OrderStatus.CANCELLED
            order.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CreateUserOrder(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=ORDER_WRITE_REQUEST,
        operation_summary="Create An Order",
        operation_description="Create an order and initiate payment via ZarinPal.",
        responses={
            201: openapi.Response(
                description="Order created successfully with payment info",
                schema=CREATE_ORDER_RESPONSE_SCHEMA,
            ),
            400: openapi.Response(
                description="Bad Request (cart empty, validation error, gateway error)",
                schema=MESSAGE_RESPONSE_SCHEMA,
            ),
            404: openapi.Response(
                description="Address not found", schema=MESSAGE_RESPONSE_SCHEMA
            ),
            500: openapi.Response(
                description="Internal Server Error", schema=MESSAGE_RESPONSE_SCHEMA
            ),
        },
    )
    def post(self, request):
        serializer = OrderWriteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            address = Address.objects.get(
                id=serializer.validated_data["address_id"],  # type: ignore
                user=request.user,
            )
        except Address.DoesNotExist:
            return Response(
                {"message": "Address not found."}, status=status.HTTP_404_NOT_FOUND
            )

        user_cart = request.user.cart
        cart_items = user_cart.items.select_related("store_item").all()
        if not cart_items:
            return Response(
                {"message": "Your cart is empty."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                for item in cart_items:
                    if item.quantity > item.store_item.stock:
                        return Response(
                            {
                                "message": f"Not enough stock for {item.store_item.product.name}"
                            },
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                total_order_price = sum(
                    item.quantity * item.store_item.total_price for item in cart_items
                )
                order = Order.objects.create(
                    customer=request.user,
                    address=address,
                    total_price=total_order_price,
                    status=Order.OrderStatus.PENDING,
                )

                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        store_item=item.store_item,
                        quantity=item.quantity,
                        price=item.store_item.price,
                        total_price=item.quantity * item.store_item.total_price,
                    )
                    item.store_item.stock -= item.quantity
                    item.store_item.save()

                transaction_id = str(randint(100000, 999999))

                payment, created = Payment.objects.get_or_create(
                    order=order,
                    defaults={
                        "transaction_id": transaction_id,
                        "amount": order.total_price,
                        "gateway": "ZarinPal",
                    },
                )

                if not created:
                    payment.transaction_id = transaction_id
                    payment.amount = order.total_price
                    payment.gateway = "ZarinPal"
                    payment.save()

                payload = {
                    "merchant_id": settings.ZARINPAL_MERCHANT_ID,
                    "amount": int(payment.amount * 10),
                    "description": f"Order #{order.pk}",
                    "callback_url": settings.ZARINPAL_CALLBACK,
                    "metadata": {
                        "mobile": str(request.user.phone) or "",
                        "email": request.user.email or "",
                    },
                }
                headers = {"Content-Type": "application/json"}
                response = requests.post(
                    settings.ZARINPAL_REQUEST_URL,
                    json=payload,
                    headers=headers,
                    timeout=10,
                )

                if not response.text.strip():
                    return Response(
                        {"message": "Empty response from payment gateway"}, status=500
                    )
                try:
                    res = response.json()
                except json.JSONDecodeError:
                    return Response(
                        {
                            "message": f"Invalid response from payment gateway: {response.text}"
                        },
                        status=500,
                    )

                if res.get("data", {}).get("code") == 100:
                    authority = res["data"]["authority"]
                    payment.transaction_id = authority
                    payment.status = Payment.PaymentStatus.PROGRESS
                    payment.save()
                    payment_url = f"{settings.ZARINPAL_STARTPAY}{authority}"
                else:
                    return Response({"message": "Payment gateway error"}, status=400)

        except Exception as e:
            import traceback

            traceback.print_exc()
            return Response({"message": f"Error happened: {str(e)}"}, status=500)

        payment_serializer = PaymentReadSerializer(payment)
        data = payment_serializer.data
        data["payment_url"] = payment_url  # type: ignore
        return Response(data, status=status.HTTP_201_CREATED)
