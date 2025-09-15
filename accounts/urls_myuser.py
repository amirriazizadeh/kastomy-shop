from django.urls import  include, path
from rest_framework.routers import DefaultRouter
from .views import UserProfileView,AddressViewSet

router = DefaultRouter()
router.register(r'addresses', AddressViewSet, basename='address')

urlpatterns = [
    path('', UserProfileView.as_view()),
    path('', include(router.urls)),
    

]