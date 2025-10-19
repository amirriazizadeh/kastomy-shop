from django.urls import path
from . import views

urlpatterns = [
    path('', views.MyCartView.as_view(), name='mycart'),  # /api/mycart/
    path('items/', views.MyCartItemsView.as_view(), name='mycart-items'),  # /api/mycart/items/
    path('add_to_cart/<int:id>/', views.AddToCartView.as_view(), name='add-to-cart'),  # /api/mycart/add_to_cart/<id>/
    path('items/<int:id>/', views.CartItemDetailView.as_view(), name='cart-item-detail'),  # /api/mycart/items/<id>/
]
