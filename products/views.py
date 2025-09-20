
from django.http import Http404
from rest_framework import viewsets,status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Product,Category
from .serializers import ProductSerializer,CategorySerializer,ProductCreateUpdateSerializer,Category,CategoryCreateUpdateSerializer
from rest_framework.permissions import IsAuthenticated,AllowAny
from .permissions import IsStaffOrReadOnly


class CategoryListCreateAPIView(APIView):
    
    permission_classes = [IsStaffOrReadOnly]

    def get(self, request, format=None):
        top_level_categories = Category.objects.filter(parent__isnull=True,is_deleted=False).prefetch_related('children')
        serializer = CategorySerializer(top_level_categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = CategoryCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            custom_response = {
                "message": "دسته‌بندی جدید با موفقیت ایجاد شد.",
                "data": serializer.data
            }
            return Response(custom_response, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryDetailAPIView(APIView):
    
    permission_classes = [IsStaffOrReadOnly]

    def get_object(self, pk):
        try:
            return Category.objects.get(pk=pk,is_deleted=False)
        except Category.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        category = self.get_object(pk)
        serializer = CategorySerializer(category) 
        return Response(serializer.data)

    def patch(self, request, pk, format=None):
        category = self.get_object(pk)
        serializer = CategoryCreateUpdateSerializer(instance=category, data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            custom_response = {
                "message": "دسته‌بندی با موفقیت آپدیت شد.",
                "data": serializer.data
            }
            return Response(custom_response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        category = self.get_object(pk)
        category_name = category.name
        category.delete()
        custom_response = {
            "message": f"دسته‌بندی '{category_name}' با موفقیت حذف شد."
        }
        return Response(custom_response, status=status.HTTP_200_OK)







# ================================================================================================
class ProductListCreateAPIView(APIView):
    
    permission_classes = [IsStaffOrReadOnly]
    def get(self, request, format=None):
        products = Product.objects.filter(is_active=True,is_deleted=False).prefetch_related(
            'category', 'images', 'variants'
        )
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = ProductCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            custom_response_data = {
                "message": "محصول جدید با موفقیت ایجاد شد.",
                "data": serializer.data
            }
            return Response(custom_response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailAPIView(APIView):

    permission_classes = [IsStaffOrReadOnly]

    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk,is_deleted=False,is_active=True)
        except Product.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        product = self.get_object(pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def patch(self, request, pk, format=None):
        product = self.get_object(pk)
        serializer = ProductCreateUpdateSerializer(instance=product, data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            custom_response_data = {
                "message": "محصول با موفقیت آپدیت شد.",
                "data": serializer.data
            }
            return Response(custom_response_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        product = self.get_object(pk)
        product_name = product.name
        product.delete()
        custom_response_data = {
            "message": f"محصول '{product_name}' با موفقیت حذف شد."
        }
        return Response(custom_response_data, status=status.HTTP_200_OK)


    
class CategoriesViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    lookup_field = 'id'

    queryset = Category.objects.filter(is_deleted=False)

    def destroy(self, request, *args, **kwargs):
        """
        Overrides the destroy method to use the model's own soft-delete method.
        """
        instance = self.get_object()
        instance.delete() 
        
        return Response({'message':'deleted product seccesfully'},status=status.HTTP_204_NO_CONTENT)