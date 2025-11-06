from django.urls import path, include
from .views import StoresView

urlpatterns = [
    path("", include("apps.reviews.urls")),
    path("accounts/", include("apps.accounts.urls")),
    path("myuser/", include("apps.users.urls")),
    path("myuser/address/", include("apps.addresses.urls")),
    path("mystore/", include("apps.stores.urls")),
    path("stores/<int:pk>/", StoresView.as_view(), name="store_id"),
    path("products/", include("apps.products.urls")),
    path("categories/", include("apps.categories.urls")),
    path("mycart/", include("apps.cart.urls")),
    path("orders/", include("apps.orders.urls")),
    path("payments/", include("apps.payments.urls")),
]
