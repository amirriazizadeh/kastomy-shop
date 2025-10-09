from django.urls import path
from .views import AddToCartView,CartView,CartDetailView

urlpatterns = [
    path('', CartView.as_view(), name='mycart'),
    path('items/<int:id>/', CartDetailView.as_view(), name='mycart-detail'),
    path('add_to_cart/<int:product_id>/', AddToCartView.as_view(), name='add-to-cart'),
]
