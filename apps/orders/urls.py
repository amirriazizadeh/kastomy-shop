from apps.orders.views import OrderListView, OrderDetailView, CreateUserOrder
from django.urls import path

urlpatterns = [
    path("", OrderListView.as_view(), name="user_orders"),
    path("<int:pk>/", OrderDetailView.as_view(), name="user_order_detail"),
    path("checkout/", CreateUserOrder.as_view(), name="user_create_order"),
]
