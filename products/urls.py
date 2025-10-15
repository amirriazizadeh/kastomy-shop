
from django.urls import path
from .views import ProductAPIView, ProductDetailAPIView

urlpatterns = [
    path('products/', ProductAPIView.as_view(), name='product-list-create'),
    path('products/<str:id>/', ProductDetailAPIView.as_view(), name='product-detail'),
]

