from django.urls import path
from .views import AddToCartView,CartView

urlpatterns = [
    path('', CartView.as_view(), name='mycart'),
    path('add_to_cart/<int:id>/', AddToCartView.as_view(), name='add-to-cart'),
]
