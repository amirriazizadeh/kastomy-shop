
from rest_framework import viewsets,status
from rest_framework.response import Response
from .models import Product,Category
from .serializers import ProductSerializer,CategorySerializer
from rest_framework.permissions import IsAuthenticated,AllowAny

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    lookup_field = 'id'

    queryset = Product.objects.filter(is_deleted=False).select_related(
        'category'
    ).prefetch_related(
        'images',
        'variants__attributes__attribute'
    )

    def get_permissions(self):
        """
        Assigns permissions based on the action.
        - Create and Destroy actions require authentication.
        - Other actions (list, retrieve, update) are allowed for anyone.
        """
        if self.action in ['create', 'destroy']:
            permission_classes = [IsAuthenticated] 
        else:
            permission_classes = [AllowAny]
            
        return [permission() for permission in permission_classes]

    def destroy(self, request, *args, **kwargs):
        """
        Overrides the destroy method to use the model's own soft-delete method.
        """
        instance = self.get_object()
        instance.delete()
        
        return Response({'message': 'deleted product successfully'}, status=status.HTTP_204_NO_CONTENT)


    
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