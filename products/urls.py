
from django.urls import path
from .views import ProductAPIView, ProductDetailAPIView

urlpatterns = [
    path('', ProductAPIView.as_view(), name='product-list-create'),
    path('<int:pk>/', ProductDetailAPIView.as_view(), name='product-detail'),
]