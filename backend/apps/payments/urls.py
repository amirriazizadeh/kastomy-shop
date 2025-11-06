from apps.payments.views import PaymentList, ZarinPalResultPayment
from django.urls import path

urlpatterns = [
    path("", PaymentList.as_view(), name="list_payments"),
    path("verify/", ZarinPalResultPayment.as_view(), name="zarinpal_result"),
]
