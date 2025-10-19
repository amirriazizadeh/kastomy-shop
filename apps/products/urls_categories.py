
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ( CategoryDetailAPIView ,CategoryListAPIView
)


urlpatterns = [
    
    path('', CategoryListAPIView.as_view(), name='category-list-create'),
    path('<int:pk>/', CategoryDetailAPIView.as_view(), name='category-detail'),
]