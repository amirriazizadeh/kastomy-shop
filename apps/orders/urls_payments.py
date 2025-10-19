

from django.urls import path
from . import views

urlpatterns = [
    path('<int:order_id>/start/', views.payment_request, name='request'),
    path('verify/', views.payment_verify , name='payment_verify'),
    # path('request/', views.request_payment, name='request_payment'),
    # path('verify/', views.verify , name='verify')
]




