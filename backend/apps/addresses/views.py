from rest_framework.permissions import IsAuthenticated
from apps.addresses.models import Address
from apps.addresses.serializers import (
    AddressWriteSerializer,
    AddressReadSerializer,
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


ADDRESS_READ_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "id": openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
        "user": openapi.Schema(type=openapi.TYPE_INTEGER, example=101),
        "street": openapi.Schema(type=openapi.TYPE_STRING, example="Avenue 42"),
        "city": openapi.Schema(type=openapi.TYPE_STRING, example="Tehran"),
        "state": openapi.Schema(type=openapi.TYPE_STRING, example="Tehran"),
        "zip_code": openapi.Schema(type=openapi.TYPE_STRING, example="1234567890"),
        "plaque": openapi.Schema(type=openapi.TYPE_STRING, example="12/A"),
        "unit": openapi.Schema(type=openapi.TYPE_INTEGER, example=3),
        "latitude": openapi.Schema(
            type=openapi.TYPE_NUMBER, format="double", example=35.7219
        ),
        "longitude": openapi.Schema(
            type=openapi.TYPE_NUMBER, format="double", example=51.3347
        ),
    },
)

ADDRESS_WRITE_REQUEST = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "street": openapi.Schema(type=openapi.TYPE_STRING, example="Avenue 42"),
        "city": openapi.Schema(type=openapi.TYPE_STRING, example="Tehran"),
        "state": openapi.Schema(type=openapi.TYPE_STRING, example="Tehran"),
        "zip_code": openapi.Schema(type=openapi.TYPE_STRING, example="1234567890"),
        "plaque": openapi.Schema(type=openapi.TYPE_STRING, example="12/A"),
        "unit": openapi.Schema(type=openapi.TYPE_INTEGER, example=3),
        "latitude": openapi.Schema(
            type=openapi.TYPE_NUMBER, format="double", example=35.7219
        ),
        "longitude": openapi.Schema(
            type=openapi.TYPE_NUMBER, format="double", example=51.3347
        ),
    },
    required=["street", "city", "state", "zip_code", "plaque"],
)


NOT_FOUND_RESPONSE = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "message": openapi.Schema(type=openapi.TYPE_STRING, example="no such address"),
    },
)


class AddressListView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="All Addresses",
        operation_description="all Addresses in list form",
        responses={
            200: openapi.Response(
                description="List of user addresses",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY, items=ADDRESS_READ_SCHEMA
                ),
            ),
        },
    )
    def get(self, request):
        user = request.user
        addresses = Address.objects.filter(user=user)
        serializer = AddressReadSerializer(addresses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=AddressWriteSerializer,
        operation_summary="Add Address For User",
        operation_description="enter your address informations",
        responses={
            201: openapi.Response(
                description="Address created successfully", schema=ADDRESS_READ_SCHEMA
            ),
            400: "Bad Request (Validation Error)",
        },
    )
    def post(self, request):
        serializer = AddressWriteSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddressDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            return Address.objects.get(pk=pk, user=user)
        except Address.DoesNotExist:
            return None

    @swagger_auto_schema(
        operation_summary="An Address",
        operation_description="see an address detail",
        responses={
            200: openapi.Response(
                description="Address details retrieved successfully",
                schema=ADDRESS_READ_SCHEMA,
            ),
            404: openapi.Response(
                description="Address not found for the user", schema=NOT_FOUND_RESPONSE
            ),
        },
    )
    def get(self, request, pk):
        address = self.get_object(pk, request.user)
        if not address:
            return Response(
                {"message": "no such address"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = AddressReadSerializer(address)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=AddressWriteSerializer,
        operation_summary="Update Address (Full)",
        operation_description="must change all details",
        responses={
            200: openapi.Response(
                description="Address updated successfully", schema=ADDRESS_READ_SCHEMA
            ),
            400: "Bad Request (Validation Error)",
            404: openapi.Response(
                description="Address not found for the user", schema=NOT_FOUND_RESPONSE
            ),
        },
    )
    def put(self, request, pk):
        address = self.get_object(pk, request.user)
        if not address:
            return Response(
                {"message": "no such address"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = AddressWriteSerializer(address, data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=AddressWriteSerializer(partial=True),
        operation_summary="Update Address (Partial)",
        operation_description="change one of the addresses detail's",
        responses={
            200: openapi.Response(
                description="Address partially updated successfully",
                schema=ADDRESS_READ_SCHEMA,
            ),
            400: "Bad Request (Validation Error)",
            404: openapi.Response(
                description="Address not found for the user", schema=NOT_FOUND_RESPONSE
            ),
        },
    )
    def patch(self, request, pk):
        address = self.get_object(pk, request.user)
        if not address:
            return Response(
                {"message": "no such address"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = AddressWriteSerializer(address, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Delete Address",
        operation_description="delete a certain address by it's pk",
        responses={
            204: openapi.Response(
                description="Address deleted successfully (No Content)",
            ),
            404: openapi.Response(
                description="Address not found for the user", schema=NOT_FOUND_RESPONSE
            ),
        },
    )
    def delete(self, request, pk):
        address = self.get_object(pk, request.user)
        if not address:
            return Response(
                {"message": "no such address"}, status=status.HTTP_404_NOT_FOUND
            )
        address.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
