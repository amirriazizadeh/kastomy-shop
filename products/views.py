
from rest_framework import viewsets,status
from rest_framework.response import Response
from .models import Product,Category
from .serializers import ProductSerializer,CategorySerializer


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    lookup_field = 'id'

    queryset = Product.objects.filter(is_deleted=False).select_related(
        'category'
    ).prefetch_related(
        'images',
        'variants__attributes__attribute'
    )

    def destroy(self, request, *args, **kwargs):
        """
        Overrides the destroy method to use the model's own soft-delete method.
        """
        instance = self.get_object()
        instance.delete() 
        
        return Response({'message':'deleted product seccesfully'},status=status.HTTP_204_NO_CONTENT)
    
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