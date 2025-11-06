from rest_framework.permissions import AllowAny
from apps.categories.models import Category
from apps.categories.serializers import CategoryReadSerializer, CategoryWriteSerializer
from rest_framework.views import APIView
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from apps.users.permissions import IsSellerUser


CATEGORY_READ_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "id": openapi.Schema(type=openapi.TYPE_INTEGER, example=5),
        "name": openapi.Schema(type=openapi.TYPE_STRING, example="Electronics"),
        "description": openapi.Schema(
            type=openapi.TYPE_STRING, example="Devices and gadgets"
        ),
        "parent": openapi.Schema(
            type=openapi.TYPE_INTEGER, example=None, description="Parent category ID"
        ),
    },
)

CATEGORY_WRITE_REQUEST = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "name": openapi.Schema(type=openapi.TYPE_STRING, example="Clothing"),
        "description": openapi.Schema(
            type=openapi.TYPE_STRING, example="Apparel and fashion items"
        ),
        "parent": openapi.Schema(
            type=openapi.TYPE_INTEGER,
            example=1,
            description="Parent category ID (optional)",
        ),
    },
    required=["name", "description"],
)

PAGINATED_CATEGORY_RESPONSE = openapi.Response(
    description="Paginated list of categories",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "count": openapi.Schema(type=openapi.TYPE_INTEGER, example=20),
            "next": openapi.Schema(
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_URI,
                example="http://api.example.com/categories?page=2",
            ),
            "previous": openapi.Schema(
                type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, example=None
            ),
            "results": openapi.Schema(
                type=openapi.TYPE_ARRAY, items=CATEGORY_READ_SCHEMA
            ),
        },
    ),
)

NOT_FOUND_RESPONSE = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "message": openapi.Schema(type=openapi.TYPE_STRING, example="no such category"),
    },
)


class CategoryListView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        else:
            return [IsSellerUser()]

    @swagger_auto_schema(
        operation_summary="All Categories",
        operation_description="all categories by list form. Supports search via 'category' query param and pagination via 'page_size'.",
        responses={
            200: PAGINATED_CATEGORY_RESPONSE,
        },
        manual_parameters=[
            openapi.Parameter(
                "category",
                openapi.IN_QUERY,
                description="Search term for category name or description",
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
        categories = Category.objects.filter(is_active=True).order_by("-id")
        search_term = request.query_params.get("category", None)
        if search_term:
            categories = categories.filter(
                Q(name__icontains=search_term) | Q(description__icontains=search_term)
            )
        paginator = PageNumberPagination()
        try:
            page_size = int(request.query_params.get("page_size", 5))
        except ValueError:
            page_size = 5

        paginator.page_size = page_size
        result_page = paginator.paginate_queryset(categories, request)
        category_data = CategoryReadSerializer(
            result_page, many=True, context={"request": request}
        ).data
        return paginator.get_paginated_response(category_data)

    @swagger_auto_schema(
        request_body=CategoryWriteSerializer,
        operation_summary="Add Category By Seller",
        operation_description="add an category by seller",
        responses={
            201: openapi.Response(
                description="Category created successfully (No content returned on success)",
            ),
            400: "Bad Request (Validation Error)",
            403: "Forbidden (Not a Seller User)",
        },
    )
    def post(self, request):
        serializer = CategoryWriteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryDetailView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        else:
            return [IsSellerUser()]

    def get_object(self, pk):
        try:
            return Category.objects.get(pk=pk,is_active=True)
        except Category.DoesNotExist:
            return None

    @swagger_auto_schema(
        operation_summary="An Category",
        operation_description="see an category detail",
        responses={
            200: openapi.Response(
                description="Category details retrieved successfully",
                schema=CATEGORY_READ_SCHEMA,
            ),
            404: openapi.Response(
                description="Category not found", schema=NOT_FOUND_RESPONSE
            ),
        },
    )
    def get(self, request, pk):
        category = self.get_object(pk)
        if not category:
            return Response(
                {"message": "no such category"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = CategoryReadSerializer(category)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=CategoryWriteSerializer,
        operation_summary="Update Category By Seller (Full)",
        operation_description="update category by seller by changing all details",
        responses={
            200: openapi.Response(
                description="Category updated successfully", schema=CATEGORY_READ_SCHEMA
            ),
            400: "Bad Request (Validation Error)",
            403: "Forbidden (Not a Seller User)",
            404: openapi.Response(
                description="Category not found", schema=NOT_FOUND_RESPONSE
            ),
        },
    )
    def put(self, request, pk):
        category = self.get_object(pk)
        if not category:
            return Response(
                {"message": "no such category"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = CategoryWriteSerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=CategoryWriteSerializer(partial=True),
        operation_summary="Update Category By Seller (Partial)",
        operation_description="update category by seller by change a single detail",
        responses={
            200: openapi.Response(
                description="Category updated successfully", schema=CATEGORY_READ_SCHEMA
            ),
            400: "Bad Request (Validation Error)",
            403: "Forbidden (Not a Seller User)",
            404: openapi.Response(
                description="Category not found", schema=NOT_FOUND_RESPONSE
            ),
        },
    )
    def patch(self, request, pk):
        category = self.get_object(pk)
        if not category:
            return Response(
                {"message": "no such category"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = CategoryWriteSerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Delete Category By Seller",
        operation_description="delete a category by seller using category's pk",
        responses={
            204: openapi.Response(
                description="Category deleted successfully (No Content)",
            ),
            403: "Forbidden (Not a Seller User)",
            404: openapi.Response(
                description="Category not found", schema=NOT_FOUND_RESPONSE
            ),
        },
    )
    def delete(self, request, pk):
        category = self.get_object(pk)
        if not category:
            return Response(
                {"message": "no such category"}, status=status.HTTP_404_NOT_FOUND
            )
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
