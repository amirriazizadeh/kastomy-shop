from rest_framework.response import Response
from rest_framework import status
from apps.users.permissions import IsSellerUser
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from apps.stores.serializers import (
    StoreReadSerializer,
    StoreWriteSerializer,
    StoreItemReadSerializer,
    StoreItemWriteSerializer,
)
from apps.stores.models import Store, StoreItem
from django.db.models import Q
from apps.addresses.serializers import AddressReadSerializer, AddressWriteSerializer
from apps.addresses.models import Address
from apps.orders.models import Order
from apps.orders.serializers import OrderStatusSerializer
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from apps.products.models import Product
from django.db import transaction
from django.db.models import F
from django.db.models.deletion import ProtectedError


class StoreProfileView(APIView):
    permission_classes = [IsSellerUser]

    @swagger_auto_schema(
        operation_summary="My Store",
        operation_description="see your store",
        responses={200: StoreReadSerializer, 404: "Not found"},
        examples={
            "application/json": {
                "id": 1,
                "name": "My Store",
                "description": "A great store",
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z",
            }
        },
    )
    def get(self, request):
        user_store = get_object_or_404(Store, seller=self.request.user)
        serializer = StoreReadSerializer(user_store)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=StoreWriteSerializer,
        operation_summary="Update Store",
        operation_description="update your store by changing all detail's",
        responses={200: StoreReadSerializer, 400: "Bad Request"},
        examples={
            "application/json": {
                "name": "Updated Store Name",
                "description": "Updated store description",
            }
        },
    )
    def put(self, request):
        user_store = get_object_or_404(Store, seller=self.request.user)
        serializer = StoreWriteSerializer(instance=user_store, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=StoreWriteSerializer,
        operation_summary="Update Store",
        operation_description="update your store by changing one detail",
        responses={200: StoreReadSerializer, 400: "Bad Request"},
        examples={"application/json": {"name": "Partially Updated Store Name"}},
    )
    def patch(self, request):
        user_store = get_object_or_404(Store, seller=self.request.user)
        serializer = StoreWriteSerializer(
            instance=user_store, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StoreAddressListView(APIView):
    permission_classes = [IsSellerUser]

    @swagger_auto_schema(
        operation_summary="All Your Store's Addresses",
        operation_description="see all of your store's addresses",
        responses={200: AddressReadSerializer(many=True), 404: "Not found"},
    )
    def get(self, request):
        user_store = Store.objects.get(seller=request.user)
        addresses = Address.objects.filter(store=user_store)
        serializer = AddressReadSerializer(addresses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=AddressWriteSerializer,
        operation_summary="Add Address For Your Store",
        operation_description="add an address for your store",
        responses={201: AddressReadSerializer, 400: "Bad Request"},
        examples={
            "application/json": {
                "street": "123 Main St",
                "city": "Tehran",
                "state": "Tehran",
                "postal_code": "1234567890",
                "country": "Iran",
            }
        },
    )
    def post(self, request):
        user_store = Store.objects.get(seller=request.user)
        serializer = AddressWriteSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save(store=user_store)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StoreAddressDetailView(APIView):
    permission_classes = [IsSellerUser]

    @swagger_auto_schema(
        request_body=AddressWriteSerializer,
        operation_summary="Update Your Store Addresses",
        operation_description="update an address from your store by changing all details",
        responses={200: AddressReadSerializer, 400: "Bad Request", 404: "Not found"},
        examples={
            "application/json": {
                "street": "456 Updated St",
                "city": "Mashhad",
                "state": "Khorasan",
                "postal_code": "9876543210",
                "country": "Iran",
            }
        },
    )
    def put(self, request, pk):
        user = request.user
        user_store = Store.objects.get(seller=user)
        try:
            store_address = Address.objects.get(user=user, store=user_store, pk=pk)
        except Address.DoesNotExist:
            return Response(
                {"message": "No address found for your store to update."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = AddressWriteSerializer(instance=store_address, data=request.data)
        if serializer.is_valid():
            serializer.save(store=user_store, user=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=AddressWriteSerializer,
        operation_summary="Update Your Store Addresses",
        operation_description="update an address from your store by changing one detail",
        responses={200: AddressReadSerializer, 400: "Bad Request", 404: "Not found"},
        examples={"application/json": {"city": "Updated City Only"}},
    )
    def patch(self, request, pk):
        user = request.user
        user_store = Store.objects.get(seller=user)
        try:
            store_address = Address.objects.get(user=user, store=user_store, pk=pk)
        except Address.DoesNotExist:
            return Response(
                {"message": "No address found for your store to update."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = AddressWriteSerializer(
            instance=store_address, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save(store=user_store, user=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Delete An Address From Your Store",
        operation_description="delete an address from your store",
        responses={
            204: "No Content",
            404: "Not found",
            400: "Bad Request - Protected Error",
        },
    )
    def delete(self, request, pk):
        user = request.user
        user_store = Store.objects.get(seller=user)
        try:
            store_address = Address.objects.get(user=user, store=user_store, pk=pk)
            store_address.delete()
        except Address.DoesNotExist:
            return Response(
                {"message": "No address found for your store to delete."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ProtectedError:
            return Response(
                {
                    "message": "This address cannot be deleted because it is linked to an order."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class StoreItemListView(APIView):
    permission_classes = [IsSellerUser]

    @swagger_auto_schema(
        operation_summary="All Items In Your Store",
        operation_description="see all of the items in your store",
        responses={
            200: StoreItemReadSerializer(many=True),
        },
    )
    def get(self, request):
        user_store = Store.objects.get(seller=request.user)
        store_items = StoreItem.objects.filter(store=user_store,is_active=True)
        search_term = request.query_params.get("search", None)
        if search_term:
            store_items = store_items.filter(
                Q(product__name__icontains=search_term)
                | Q(product__description__icontains=search_term)
            )
        paginator = PageNumberPagination()
        paginator.page_size = int(request.query_params.get("page_size", 5))  # type: ignore
        result_page = paginator.paginate_queryset(store_items, request)
        data = StoreItemReadSerializer(result_page, many=True).data
        return paginator.get_paginated_response(data)

    @swagger_auto_schema(
        request_body=StoreItemWriteSerializer,
        operation_summary="Add An Product As Item To Your Store",
        operation_description="add an product as item to your store",
        responses={201: StoreItemReadSerializer, 400: "Bad Request - Not enough stock"},
        examples={
            "application/json": {"product": 1, "stock": 50, "price": "100000.00"}
        },
    )
    def post(self, request):
        user = request.user
        user_store = Store.objects.get(seller=user)
        with transaction.atomic():
            serializer = StoreItemWriteSerializer(data=request.data)
            if serializer.is_valid():
                stock = serializer.validated_data["stock"]  # type: ignore
                product = serializer.validated_data["product"]  # type: ignore
                product = Product.objects.select_for_update().get(pk=product.pk)
                if product.stock >= stock:
                    product.stock = F("stock") - stock
                    product.save()
                    serializer.save(store=user_store)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response(
                        {"message": "not enough product stock"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StoreItemDetailView(APIView):
    permission_classes = [IsSellerUser]

    @swagger_auto_schema(
        operation_summary="See An Item In Your Store",
        operation_description="see an item in your store by it's pk",
        responses={200: StoreItemReadSerializer, 404: "Not found"},
    )
    def get(self, request, pk):
        user_store = Store.objects.get(seller=request.user)
        try:
            store_item = StoreItem.objects.get(pk=pk, store=user_store,is_active=True)
        except StoreItem.DoesNotExist:
            return Response(
                {"message": "no such Store item"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = StoreItemReadSerializer(store_item)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=StoreItemWriteSerializer,
        operation_summary="Update An Item In Your Store",
        operation_description="update an item in your store by changing all of it's details",
        responses={200: StoreItemReadSerializer, 400: "Bad Request", 404: "Not found"},
        examples={
            "application/json": {"product": 1, "stock": 75, "price": "120000.00"}
        },
    )
    def put(self, request, pk):
        user = request.user
        user_store = Store.objects.get(seller=user)
        try:
            store_item = StoreItem.objects.get(pk=pk, store=user_store)
        except StoreItem.DoesNotExist:
            return Response(
                {"message": "no such Store item for your store"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = StoreItemWriteSerializer(instance=store_item, data=request.data)
        if serializer.is_valid():
            serializer.save(store=user_store)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=StoreItemWriteSerializer,
        operation_summary="Update An Item In Your Store",
        operation_description="update an item in your store by changing one of it's details",
        responses={200: StoreItemReadSerializer, 400: "Bad Request", 404: "Not found"},
        examples={"application/json": {"price": "150000.00"}},
    )
    def patch(self, request, pk):
        user = request.user
        user_store = Store.objects.get(seller=user)
        try:
            store_item = StoreItem.objects.get(pk=pk, store=user_store)
        except StoreItem.DoesNotExist:
            return Response(
                {"message": "no such Store item for your store"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = StoreItemWriteSerializer(
            instance=store_item, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save(store=user_store)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Delete An Item From Your Store",
        operation_description="delete an item from your store by it's pk",
        responses={204: "No Content", 404: "Not found"},
    )
    def delete(self, request, pk):
        user = request.user
        user_store = Store.objects.get(seller=user)

        with transaction.atomic():
            try:
                store_item = StoreItem.objects.select_for_update().get(
                    pk=pk, store=user_store
                )
                product = Product.objects.select_for_update().get(
                    pk=store_item.product.pk
                )
                product.stock = F("stock") + store_item.stock
                product.save()
                store_item.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)

            except StoreItem.DoesNotExist:
                return Response(
                    {"message": "no item found"},
                    status=status.HTTP_404_NOT_FOUND,
                )


class StoreOrderListView(APIView):
    permission_classes = [IsSellerUser]

    @swagger_auto_schema(
        operation_summary="All Your Store's Orders",
        operation_description="all orders from your store",
        responses={200: OrderStatusSerializer(many=True)},
    )
    def get(self, request):
        user_store = get_object_or_404(Store, seller=self.request.user)
        user_orders = Order.objects.filter(
            items__store_item__store=user_store
        ).distinct()

        search_term = request.query_params.get("search", None)
        if search_term:
            user_orders = user_orders.filter(
                Q(items__store_item__product__description__icontains=search_term)
                | Q(items__store_item__product__name__icontains=search_term)
            )

        paginator = PageNumberPagination()
        paginator.page_size = int(request.query_params.get("page_size", 10))
        result_page = paginator.paginate_queryset(user_orders, request)
        serializer = OrderStatusSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class StoreOrderDetailView(APIView):
    permission_classes = [IsSellerUser]

    @swagger_auto_schema(
        operation_summary="An Order From Your Store",
        operation_description="see detail's of an order from your store",
        responses={200: OrderStatusSerializer, 404: "Not found"},
    )
    def get(self, request, pk):
        user_store = get_object_or_404(Store, seller=self.request.user)
        try:
            order = Order.objects.get(pk=pk, items__store_item__store=user_store)
        except Order.DoesNotExist:
            return Response(
                {"message": "No such order found for your store"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = OrderStatusSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChangeOrderStatusView(APIView):
    permission_classes = [IsSellerUser]

    @swagger_auto_schema(
        request_body=OrderStatusSerializer,
        operation_summary="Change Status Of An Order From your Store",
        operation_description="change to done if you wanna that user pay it's payment",
        responses={200: OrderStatusSerializer, 400: "Bad Request", 404: "Not found"},
        examples={"application/json": {"status": "completed"}},
    )
    def post(self, request, pk):
        user_store = get_object_or_404(Store, seller=self.request.user)
        try:
            order = Order.objects.get(pk=pk, items__store_item__store=user_store)
        except Order.DoesNotExist:
            return Response(
                {"message": "No such order found for your store"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = OrderStatusSerializer(
            instance=order, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
