from celery import shared_task
from django.core.mail import send_mail


@shared_task
def send_payment_success_email(email, order_id):
    send_mail(
        "Payment Success",
        f"You paid successfully for order {order_id}",
        "noreply@example.com",
        [email],
        fail_silently=False,
    )
