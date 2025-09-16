from django.urls import  include, path
from rest_framework.routers import DefaultRouter
from .views import UserProfileView,AddressViewSet,SellerRegistrationAPIView

router = DefaultRouter()
router.register(r'address', AddressViewSet, basename='address')

urlpatterns = [
    path('', UserProfileView.as_view()),
    path('register_as_seller/', SellerRegistrationAPIView.as_view()),
    path('', include(router.urls)),
    

]