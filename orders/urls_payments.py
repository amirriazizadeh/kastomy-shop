

from django.urls import path
from . import views

urlpatterns = [
    path('<int:order_id>/start/', views.PaymentRequestAPIView.as_view(), name='request'),
    path('verify/', views.VerifyPaymentAPIView.as_view() , name='payment_verify'),
    # path('request/', views.request_payment, name='request_payment'),
    # path('verify/', views.verify , name='verify')
]




