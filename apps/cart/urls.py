from django.urls import path
from apps.cart.views import UserCart,UserCartItem, CartItemDetail, AddStoreItemToCart

urlpatterns = [
    path("", UserCart.as_view(), name="user_cart"),
    path("items/", UserCartItem.as_view(), name="user_cart_items"),
    path("items/<int:pk>/", CartItemDetail.as_view(), name="user_cart_item_detail"),
    path(
        "add_to_cart/<int:pk>/",
        AddStoreItemToCart.as_view(),
        name="add_store_item_to_cart",
    ),
    
]
