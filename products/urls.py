
# from django.urls import path
# from .views import ProductAPIView, ProductDetailAPIView

# urlpatterns = [
#     path('', ProductAPIView.as_view(), name='product-list-create'),
#     path('<int:pk>/', ProductDetailAPIView.as_view(), name='product-detail'),
# ]

# shop/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
]
