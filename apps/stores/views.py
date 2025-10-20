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

