from django.urls import path
from apps.cart.views import UserCart,UserCartItem, CartItemDetail

urlpatterns = [
    path("", UserCart.as_view(), name="user_cart"),
    path("items/", UserCartItem.as_view(), name="user_cart_items"),
    path("items/<int:pk>/", CartItemDetail.as_view(), name="user_cart_item_detail"),
    
    
]
