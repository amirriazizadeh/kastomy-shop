from .serializers import (
    ReviewProductReadSerializer,
    ReviewProductWriteSerializer,
    ReviewStoreReadSerializer,
    ReviewStoreWriteSerializer
)
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from apps.reviews.models import Review
from apps.products.models import Product
from apps.stores.models import Store
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


REVIEW_PRODUCT_READ_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "id": openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
        "user": openapi.Schema(type=openapi.TYPE_INTEGER, example=10),
        "product": openapi.Schema(type=openapi.TYPE_INTEGER, example=20),
        "rating": openapi.Schema(type=openapi.TYPE_INTEGER, example=5),
        "comment": openapi.Schema(type=openapi.TYPE_STRING, example="Great product!"),
        "created_at": openapi.Schema(
            type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME
        ),
    },
)

REVIEW_STORE_READ_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "id": openapi.Schema(type=openapi.TYPE_INTEGER, example=2),
        "user": openapi.Schema(type=openapi.TYPE_INTEGER, example=11),
        "store": openapi.Schema(type=openapi.TYPE_INTEGER, example=30),
        "rating": openapi.Schema(type=openapi.TYPE_INTEGER, example=4),
        "comment": openapi.Schema(
            type=openapi.TYPE_STRING, example="Good service, but delivery was slow."
        ),
        "created_at": openapi.Schema(
            type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME
        ),
    },
)



def get_paginated_response_schema(result_schema):
    return openapi.Response(
        description="Paginated list of reviews",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "count": openapi.Schema(type=openapi.TYPE_INTEGER, example=10),
                "next": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_URI,
                    example="http://api.example.com/reviews?page=2&page_size=5",
                ),
                "previous": openapi.Schema(
                    type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, example=None
                ),
                "results": openapi.Schema(type=openapi.TYPE_ARRAY, items=result_schema),
            },
        ),
    )


PAGINATED_PRODUCT_REVIEW_RESPONSE = get_paginated_response_schema(
    REVIEW_PRODUCT_READ_SCHEMA
)
PAGINATED_STORE_REVIEW_RESPONSE = get_paginated_response_schema(
    REVIEW_STORE_READ_SCHEMA
)

NOT_FOUND_RESPONSE = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "message": openapi.Schema(
            type=openapi.TYPE_STRING, example="no such product/store"
        ),
    },
)


class ProductReviewListView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="All Product's Reviews",
        operation_description="all product's reviews in list form. Filterable by 'search' query param (comment, product name/description).",
        responses={
            200: PAGINATED_PRODUCT_REVIEW_RESPONSE,
            404: openapi.Response(
                description="Product not found", schema=NOT_FOUND_RESPONSE
            ),
        },
        manual_parameters=[
            openapi.Parameter(
                "search",
                openapi.IN_QUERY,
                description="Search term for review comments or product name/description",
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
    def get(self, request, product_id):
        try:
            Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response(
                {"message": "no such product"}, status=status.HTTP_404_NOT_FOUND
            )

        product_reviews = Review.objects.filter(product_id=product_id)
        search_term = request.query_params.get("search", None)
        if search_term:
            product_reviews = product_reviews.filter(
                Q(comment__icontains=search_term)
                | Q(product__description__icontains=search_term)
                | Q(product__name__icontains=search_term)
            )
        paginator = PageNumberPagination()
        try:
            page_size = int(request.query_params.get("page_size", 5))
        except ValueError:
            page_size = 5

        paginator.page_size = page_size
        result_page = paginator.paginate_queryset(product_reviews, request)
        data = ReviewProductReadSerializer(
            result_page, many=True, context={"request": request}
        ).data
        return paginator.get_paginated_response(data)


class StoreReviewListView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="All Store's Reviews",
        operation_description="all store's reviews in list form. Filterable by 'search' query param (comment, store name/description).",
        responses={
            200: PAGINATED_STORE_REVIEW_RESPONSE,
            404: openapi.Response(
                description="Store not found", schema=NOT_FOUND_RESPONSE
            ),
        },
        manual_parameters=[
            openapi.Parameter(
                "search",
                openapi.IN_QUERY,
                description="Search term for review comments or store name/description",
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
    def get(self, request, store_id):
        try:
            store = Store.objects.get(pk=store_id)
        except Store.DoesNotExist:
            return Response(
                {"message": "no such store"}, status=status.HTTP_404_NOT_FOUND
            )

        store_reviews = Review.objects.filter(store=store)
        search_term = request.query_params.get("search", None)
        if search_term:
            store_reviews = store_reviews.filter(
                Q(comment__icontains=search_term)
                | Q(store__description__icontains=search_term)
                | Q(store__name__icontains=search_term)
            )
        paginator = PageNumberPagination()
        try:
            page_size = int(request.query_params.get("page_size", 5))
        except ValueError:
            page_size = 5

        paginator.page_size = page_size
        result_page = paginator.paginate_queryset(store_reviews, request)
        data = ReviewStoreReadSerializer(result_page, many=True).data
        return paginator.get_paginated_response(data)


class ProductReviewCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=ReviewProductWriteSerializer,
        operation_summary="Create Review For A Product",
        operation_description="create a review for a product using product_id from the URL path.",
        responses={
            201: openapi.Response(
                description="Review created successfully",
                schema=REVIEW_PRODUCT_READ_SCHEMA,
            ),
            400: "Bad Request (Validation Error)",
            401: "Unauthorized",
        },
    )
    def post(self, request, product_id):
        data = request.data.copy()
        data["product_id"] = product_id

        serializer = ReviewProductWriteSerializer(
            data=data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save(user=request.user)  
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StoreReviewCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=ReviewStoreWriteSerializer,
        operation_summary="Create Review For A Store",
        operation_description="create a review for a store using store_id from the URL path.",
        responses={
            201: openapi.Response(
                description="Review created successfully",
                schema=REVIEW_STORE_READ_SCHEMA,
            ),
            400: "Bad Request (Validation Error)",
            401: "Unauthorized",
        },
    )
    def post(self, request, store_id):
        data = request.data.copy()
        data["store_id"] = store_id

        serializer = ReviewStoreWriteSerializer(data=data, context={"request": request})
        if serializer.is_valid():
            serializer.save(user=request.user) 
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
