from django.urls import path
from apps.stores.views import (
    StoreProfileView,
    StoreAddressListView,
    StoreAddressDetailView,
    
)

urlpatterns = [
    path("", StoreProfileView.as_view(), name="my-store-profile"),
    path("address/", StoreAddressListView.as_view(), name="store_address_list_create"),
    path("address/<int:pk>/", StoreAddressDetailView.as_view(), name="store_address_detail_update_delete"),
    
]