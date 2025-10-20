from django.urls import path
from apps.products.views import ProductListView, ProductDetailView

urlpatterns = [
    path("", ProductListView.as_view(), name="products_list_create"),
    path("<int:pk>/", ProductDetailView.as_view(), name="products_detail_update_delete"),
]