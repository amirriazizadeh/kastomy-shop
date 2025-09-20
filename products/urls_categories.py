# product/urls.py or your_project/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductListCreateAPIView, ProductDetailAPIView,
    CategoryListCreateAPIView, CategoryDetailAPIView # ویوهای جدید را ایمپورت کنید
)


urlpatterns = [
    
    path('', CategoryListCreateAPIView.as_view(), name='category-list-create'),
    path('<int:pk>/', CategoryDetailAPIView.as_view(), name='category-detail'),
]