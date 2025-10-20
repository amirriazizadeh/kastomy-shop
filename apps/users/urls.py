from django.urls import path
from .views import (
    MyUserView,
    SellerRegistrationView,
    DeleteRegistration,
    ResetPassword,
)

urlpatterns = [
    path("", MyUserView.as_view(), name="myuser"),
    path(
        "register_as_seller/",
        SellerRegistrationView.as_view(),
        name="register_as_seller",
    ),
    path(
        "register_as_not_seller/",
        DeleteRegistration.as_view(),
        name="register_as_not_seller",
    ),
    path("reset_password/", ResetPassword.as_view(), name="reset_password"),
]
