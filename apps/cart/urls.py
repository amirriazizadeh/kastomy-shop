from django.urls import path
from apps.cart.views import UserCart

urlpatterns = [
    path("", UserCart.as_view(), name="user_cart"),
    
]
