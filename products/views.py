
from django.http import Http404
from rest_framework import viewsets,status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Product,Category
from .serializers import ProductSerializer,CategorySerializer,ProductCreateUpdateSerializer,Category,CategoryCreateUpdateSerializer
from rest_framework.permissions import IsAuthenticated,AllowAny
from .permissions import IsStaffOrReadOnly
from drf_spectacular.utils import extend_schema, OpenApiExample



class CategoryListCreateAPIView(APIView):
    """
    خواندن همه دسته بندی ها و ساخت دسته بندی جدید.
    """
    permission_classes = [IsStaffOrReadOnly]

    @extend_schema(
        responses=CategorySerializer(many=True)  # خروجی GET
    )
    def get(self, request, format=None):
        top_level_categories = Category.objects.filter(
            parent__isnull=True,
            is_deleted=False
        ).prefetch_related('children')
        serializer = CategorySerializer(top_level_categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=CategoryCreateUpdateSerializer,   # بدنه ورودی
        responses={
            201: CategorySerializer,              # خروجی موفق
            400: dict                             # خطا
        }
    )
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
    """
    مدیریت عملیات CRUD روی یک دسته‌بندی خاص.

    متدها:
        - GET: دریافت اطلاعات یک دسته‌بندی
        - PATCH: ویرایش بخشی از یک دسته‌بندی
        - DELETE: حذف یک دسته‌بندی
    """
    permission_classes = [IsStaffOrReadOnly]

    def get_object(self, pk):
        """دریافت آبجکت دسته‌بندی یا بازگرداندن خطای 404 در صورت نبودن"""
        try:
            return Category.objects.get(pk=pk, is_deleted=False)
        except Category.DoesNotExist:
            raise Http404

    @extend_schema(
        summary="دریافت یک دسته‌بندی",
        description="این متد اطلاعات کامل یک دسته‌بندی خاص را برمی‌گرداند.",
        responses={200: CategorySerializer, 404: dict}
    )
    def get(self, request, pk, format=None):
        category = self.get_object(pk)
        serializer = CategorySerializer(category) 
        return Response(serializer.data)

    @extend_schema(
        summary="ویرایش دسته‌بندی",
        description="این متد امکان ویرایش بخشی از اطلاعات دسته‌بندی (Partial Update) را فراهم می‌کند.",
        request=CategoryCreateUpdateSerializer,
        responses={200: CategorySerializer, 400: dict, 404: dict}
    )
    def patch(self, request, pk, format=None):
        category = self.get_object(pk)
        serializer = CategoryCreateUpdateSerializer(
            instance=category, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            custom_response = {
                "message": "دسته‌بندی با موفقیت آپدیت شد.",
                "data": serializer.data
            }
            return Response(custom_response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="حذف دسته‌بندی",
        description="این متد یک دسته‌بندی را بر اساس شناسه (ID) حذف می‌کند.",
        responses={200: dict, 404: dict}
    )
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
    """
    لیست و ایجاد محصول.

    - `GET`: نمایش لیست محصولات فعال (is_active=True) و غیرحذف‌شده (is_deleted=False)  
    - `POST`: ایجاد محصول جدید (فقط برای ادمین/استف).  
    """
    permission_classes = [IsStaffOrReadOnly]

    @extend_schema(
        summary="لیست محصولات",
        description="این متد تمام محصولات فعال و غیرحذف‌شده را برمی‌گرداند.",
        responses={200: ProductSerializer(many=True)},
        tags=["Products"]
    )
    def get(self, request, format=None):
        products = Product.objects.filter(
            is_active=True,
            is_deleted=False
        ).prefetch_related('category', 'images', 'variants')
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="ایجاد محصول جدید",
        description="این متد یک محصول جدید ایجاد می‌کند. تنها کاربران ادمین یا استاف اجازه استفاده دارند.",
        request=ProductCreateUpdateSerializer,
        responses={
            201: ProductSerializer,
            400: {"description": "خطا در اعتبارسنجی داده‌ها"}
        },
        examples=[
            OpenApiExample(
                "نمونه محصول جدید",
                description="نمونه‌ای از داده‌هایی که برای ایجاد محصول ارسال می‌شود.",
                value={
                    "name": "Laptop Lenovo IdeaPad",
                    "description": "یک لپ‌تاپ سبک و قدرتمند مناسب برای کار روزمره.",
                    "price": 18500000,
                    "category": 1,
                    "is_active": True
                },
                request_only=True
            )
        ],
        tags=["Products"]
    )
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
    """
    جزئیات یک محصول خاص (GET, PATCH, DELETE).

    - `GET`: دریافت جزئیات یک محصول  
    - `PATCH`: ویرایش اطلاعات محصول (فقط برای استاف/ادمین)  
    - `DELETE`: حذف یک محصول (soft delete یا واقعی، بسته به مدل)  
    """
    permission_classes = [IsStaffOrReadOnly]

    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk, is_deleted=False, is_active=True)
        except Product.DoesNotExist:
            raise Http404

    @extend_schema(
        summary="دریافت جزئیات محصول",
        description="با دادن `id` محصول، جزئیات آن را دریافت کنید.",
        responses={200: ProductSerializer, 404: {"description": "محصول یافت نشد."}},
        tags=["Products"]
    )
    def get(self, request, pk, format=None):
        product = self.get_object(pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    @extend_schema(
        summary="ویرایش محصول",
        description="ویرایش بخشی از اطلاعات محصول (partial update).",
        request=ProductCreateUpdateSerializer,
        responses={
            200: ProductSerializer,
            400: {"description": "خطا در اعتبارسنجی داده‌ها"},
            404: {"description": "محصول یافت نشد"}
        },
        examples=[
            OpenApiExample(
                "نمونه ویرایش محصول",
                description="مثالی از تغییر قیمت محصول.",
                value={
                    "price": 21000000,
                    "description": "نسخه جدید لپ‌تاپ با باتری بهتر."
                },
                request_only=True
            )
        ],
        tags=["Products"]
    )
    def patch(self, request, pk, format=None):
        product = self.get_object(pk)
        serializer = ProductCreateUpdateSerializer(
            instance=product, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            custom_response_data = {
                "message": "محصول با موفقیت آپدیت شد.",
                "data": serializer.data
            }
            return Response(custom_response_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="حذف محصول",
        description="محصول مشخص شده را حذف می‌کند.",
        responses={
            200: {"description": "محصول با موفقیت حذف شد."},
            404: {"description": "محصول یافت نشد"}
        },
        tags=["Products"]
    )
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