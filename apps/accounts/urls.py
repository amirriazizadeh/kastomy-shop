from django.urls import path
from .views import (
    
    TokenObtainPairViewSwagger,
    LogoutView,
    Register,
)


urlpatterns = [
    path("login/", TokenObtainPairViewSwagger.as_view(), name="token_obtain_pair"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", Register.as_view(), name="register"),

    
]
