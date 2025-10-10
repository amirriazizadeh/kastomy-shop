
from django.http import Http404
from rest_framework import viewsets,status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Product,Category
from .serializers import ProductSerializer,Category,CategorySerializer,ProductDetailsSerializer
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.pagination import PageNumberPagination




# ================================================================================================



class CategoryListAPIView(APIView):

    def get(self, request):
        categories = Category.objects.all().prefetch_related('children', 'parent')
        paginator = PageNumberPagination()
        paginator.page_size = 10  # یا هر اندازه‌ای که خواستی
        result_page = paginator.paginate_queryset(categories, request)
        serializer = CategorySerializer(result_page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = CategorySerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryDetailAPIView(APIView):

    def get_object(self, pk):
        try:
            return Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return None

    def get(self, request, pk):
        category = self.get_object(pk)
        if not category:
            return Response({'detail': 'دسته پیدا نشد.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = CategorySerializer(category, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        category = self.get_object(pk)
        if not category:
            return Response({'detail': 'دسته پیدا نشد.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = CategorySerializer(category, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        category = self.get_object(pk)
        if not category:
            return Response({'detail': 'دسته پیدا نشد.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = CategorySerializer(category, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        category = self.get_object(pk)
        if not category:
            return Response({'detail': 'دسته پیدا نشد.'}, status=status.HTTP_404_NOT_FOUND)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(is_active=True).select_related('category', 'best_seller').prefetch_related('images', 'sellers')

    def get_serializer_class(self):
        if self.action == 'retrieve':  # /products/<id>/
            return ProductDetailsSerializer
        return ProductSerializer  # /products/
# class ProductAPIView(APIView):
#     permission_classes = [AllowAny]

#     def get(self, request):
#         products = Product.objects.select_related('category', 'best_seller').all()

#         # ✳️ فعال کردن pagination
#         paginator = PageNumberPagination()
#         paginator.page_size = 10  # می‌تونی مقدار پیش‌فرض رو تنظیم یا از settings بگیری

#         # ✳️ اعمال صفحه‌بندی روی queryset
#         result_page = paginator.paginate_queryset(products, request)

#         # ✳️ serialize داده‌ها
#         serializer = ProductSerializer(result_page, many=True, context={'request': request})

#         # ✳️ برگردوندن پاسخ صفحه‌بندی‌شده (count, next, previous, results)
#         return paginator.get_paginated_response(serializer.data)

#     def post(self, request):
#         serializer = ProductSerializer(data=request.data, context={'request': request})
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class ProductDetailAPIView(APIView):
#     permission_classes = [AllowAny]

#     def get_object(self, pk):
#         try:
#             return Product.objects.select_related('category', 'best_seller').get(pk=pk)
#         except Product.DoesNotExist:
#             return None

#     def get(self, request, pk):
#         product = self.get_object(pk)
#         if not product:
#             return Response({'detail': 'محصول پیدا نشد.'}, status=status.HTTP_404_NOT_FOUND)
#         serializer = ProductDetailsSerializer(product, context={'request': request})
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     def put(self, request, pk):
#         product = self.get_object(pk)
#         if not product:
#             return Response({'detail': 'محصول پیدا نشد.'}, status=status.HTTP_404_NOT_FOUND)
#         serializer = ProductSerializer(product, data=request.data, context={'request': request})
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def patch(self, request, pk):
#         product = self.get_object(pk)
#         if not product:
#             return Response({'detail': 'محصول پیدا نشد.'}, status=status.HTTP_404_NOT_FOUND)
#         serializer = ProductSerializer(product, data=request.data, partial=True, context={'request': request})
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request, pk):
#         product = self.get_object(pk)
#         if not product:
#             return Response({'detail': 'محصول پیدا نشد.'}, status=status.HTTP_404_NOT_FOUND)
#         product.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)