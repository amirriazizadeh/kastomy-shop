from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from apps.products.serializers import ProductReadSerializer, ProductWriteSerializer
from apps.products.models import Product
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from apps.users.permissions import IsSellerUser


PRODUCT_IMAGE_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "id": openapi.Schema(type=openapi.TYPE_INTEGER, example=101),
        "image": openapi.Schema(
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_URI,
            example="/media/products/img_1.jpg",
        ),
    },
)

PRODUCT_READ_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "id": openapi.Schema(type=openapi.TYPE_INTEGER, example=15),
        "name": openapi.Schema(type=openapi.TYPE_STRING, example="Laptop Model X"),
        "description": openapi.Schema(
            type=openapi.TYPE_STRING, example="High-performance computing device."
        ),
        "category": openapi.Schema(
            type=openapi.TYPE_INTEGER, example=5, description="Category ID"
        ),
        "attributes": openapi.Schema(
            type=openapi.TYPE_STRING, example='{"color": "black", "size": "15 inch"}'
        ),
        "created_by": openapi.Schema(
            type=openapi.TYPE_INTEGER, example=10, description="Seller User ID"
        ),
        "images": openapi.Schema(type=openapi.TYPE_ARRAY, items=PRODUCT_IMAGE_SCHEMA),
    },
)

PRODUCT_WRITE_REQUEST = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "name": openapi.Schema(type=openapi.TYPE_STRING, example="Laptop Model X"),
        "description": openapi.Schema(
            type=openapi.TYPE_STRING, example="High-performance computing device."
        ),
        "category": openapi.Schema(
            type=openapi.TYPE_INTEGER,
            example=5,
            description="ID of the product category",
        ),
        "attributes": openapi.Schema(
            type=openapi.TYPE_STRING,
            example='{"color": "black", "size": "15 inch"}',
            description="JSON string of product attributes",
        ),
        "uploaded_images": openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(type=openapi.TYPE_FILE),
            description="Images to upload for the product (Multi-part/form-data)",
        ),
    },
    required=["name", "description", "category"],
)

PAGINATED_PRODUCT_RESPONSE = openapi.Response(
    description="Paginated list of products",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "count": openapi.Schema(type=openapi.TYPE_INTEGER, example=20),
            "next": openapi.Schema(
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_URI,
                example="http://api.example.com/products?page=2",
            ),
            "previous": openapi.Schema(
                type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, example=None
            ),
            "results": openapi.Schema(
                type=openapi.TYPE_ARRAY, items=PRODUCT_READ_SCHEMA
            ),
        },
    ),
)

NOT_FOUND_RESPONSE = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "message": openapi.Schema(type=openapi.TYPE_STRING, example="no such product"),
    },
)


class ProductListView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsSellerUser()]

    @swagger_auto_schema(
        operation_summary="All Products",
        operation_description="all products in list form. Supports search via 'name' query param (name/description) and pagination via 'page_size'.",
        responses={
            200: PAGINATED_PRODUCT_RESPONSE,
        },
        manual_parameters=[
            openapi.Parameter(
                "name",
                openapi.IN_QUERY,
                description="Search term for product name or description",
                type=openapi.TYPE_STRING,
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
        products = Product.objects.filter(is_active=True).order_by("-id")
        search_term = request.query_params.get("name", "")
        if search_term:
            products = products.filter(
                Q(name__icontains=search_term) | Q(description__icontains=search_term)
            )
        paginator = PageNumberPagination()
        try:
            page_size = int(request.query_params.get("page_size", 5))  # type: ignore
        except ValueError:
            page_size = 5

        paginator.page_size = page_size
        result_page = paginator.paginate_queryset(products, request)
        data = ProductReadSerializer(
            result_page, many=True, context={"request": request}
        ).data
        return paginator.get_paginated_response(data)

    @swagger_auto_schema(
        request_body=PRODUCT_WRITE_REQUEST,
        operation_summary="Add Product By Seller",
        operation_description="add product by seller (Requires Multi-part/form-data for images).",
        consumes=["multipart/form-data"],
        responses={
            201: openapi.Response(
                description="Product created successfully", schema=PRODUCT_READ_SCHEMA
            ),
            400: "Bad Request (Validation Error)",
            403: "Forbidden (Not a Seller User)",
        },
    )
    def post(self, request):
        data = request.data.copy()
        images = request.FILES.getlist("uploaded_images")
        if images:
            data.setlist("uploaded_images", images)
        serializer = ProductWriteSerializer(data=data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsSellerUser()]

    @swagger_auto_schema(
        operation_summary="An Product",
        operation_description="an product details by it's pk",
        responses={
            200: openapi.Response(
                description="Product details retrieved successfully",
                schema=PRODUCT_READ_SCHEMA,
            ),
            404: openapi.Response(
                description="Product not found", schema=NOT_FOUND_RESPONSE
            ),
        },
    )
    def get(self, request, pk):
        try:
            product = Product.objects.get(pk=pk, is_active=True)
        except Product.DoesNotExist:
            return Response(
                {"message": "no such product"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = ProductReadSerializer(product, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=PRODUCT_WRITE_REQUEST,
        operation_summary="Update Product By Seller (Full)",
        operation_description="update all product's details by seller (Requires Multi-part/form-data for images, all fields are required for PUT).",
        consumes=["multipart/form-data"],
        responses={
            200: openapi.Response(
                description="Product updated successfully", schema=PRODUCT_READ_SCHEMA
            ),
            400: "Bad Request (Validation Error)",
            403: "Forbidden (Not a Seller User)",
            404: openapi.Response(
                description="Product not found", schema=NOT_FOUND_RESPONSE
            ),
        },
    )
    def put(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response(
                {"message": "no such product"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = ProductWriteSerializer(
            product, data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=ProductWriteSerializer(partial=True),
        operation_summary="Update Product By Seller (Partial)",
        operation_description="update product's one detail by seller (Requires Multi-part/form-data for images, fields are optional for PATCH).",
        consumes=["multipart/form-data"],
        responses={
            200: openapi.Response(
                description="Product updated successfully", schema=PRODUCT_READ_SCHEMA
            ),
            400: "Bad Request (Validation Error)",
            403: "Forbidden (Not a Seller User)",
            404: openapi.Response(
                description="Product not found", schema=NOT_FOUND_RESPONSE
            ),
        },
    )
    def patch(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response(
                {"message": "no such product"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = ProductWriteSerializer(
            product,
            data=request.data,
            context={"request": request},
            partial=True,
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Delete Product By Seller",
        operation_description="delete a product by seller using it's pk",
        responses={
            204: openapi.Response(
                description="Product deleted successfully (No Content)",
            ),
            403: "Forbidden (Not a Seller User)",
            404: openapi.Response(
                description="Product not found", schema=NOT_FOUND_RESPONSE
            ),
        },
    )
    def delete(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response(
                {"message": "no such product"}, status=status.HTTP_404_NOT_FOUND
            )
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
