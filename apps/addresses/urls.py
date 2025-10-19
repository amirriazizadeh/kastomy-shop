from django.urls import path
from apps.addresses.views import AddressListView, AddressDetailView

urlpatterns = [
    path("", AddressListView.as_view(), name="address_list_create"),
    path("<int:pk>/", AddressDetailView.as_view(), name="address_detail_update_delete"),
]
