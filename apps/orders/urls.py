

from django.urls import path
from . import views

urlpatterns = [
    path('',views.OrdersView.as_view()),
    path('checkout/',views.CheckoutAPIView.as_view()),
    
]




