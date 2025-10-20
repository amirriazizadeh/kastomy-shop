from django.urls import path
from apps.stores.views import (
    StoreProfileView,
    StoreAddressListView,
    StoreAddressDetailView,
    StoreItemListView,
    StoreItemDetailView,
    StoreOrderListView,
    StoreOrderDetailView,
    ChangeOrderStatusView,
)

urlpatterns = [
    path("", StoreProfileView.as_view(), name="my-store-profile"),
    path("address/", StoreAddressListView.as_view(), name="store_address_list_create"),
    path("address/<int:pk>/", StoreAddressDetailView.as_view(), name="store_address_detail_update_delete"),
    path("items/", StoreItemListView.as_view(), name="store_item_list_create"),
    path("items/<int:pk>/", StoreItemDetailView.as_view(), name="store_item_detail_update_delete"),
    path("orders/", StoreOrderListView.as_view(), name="store_order_list"),
    path("orders/<int:pk>/", StoreOrderDetailView.as_view(), name="store_order_detail"),
    path("orders/change-status/<int:pk>/", ChangeOrderStatusView.as_view(), name="store_order_change_status"),
]