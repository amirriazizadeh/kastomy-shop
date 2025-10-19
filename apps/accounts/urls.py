from django.urls import path
from .views import (
    
    TokenObtainPairViewSwagger,
    LogoutView,
    Register,
    TokenRefreshViewSwagger,
    RequestOtp,
    VerifyOtp,
)


urlpatterns = [
    path("login/", TokenObtainPairViewSwagger.as_view(), name="token_obtain_pair"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", Register.as_view(), name="register"),
    path("token/refresh/", TokenRefreshViewSwagger.as_view(), name="token_refresh"),
    path("request-otp/", RequestOtp.as_view(), name="request_otp"),
    path("verify-otp/", VerifyOtp.as_view(), name="verify_otp"),

    
]
