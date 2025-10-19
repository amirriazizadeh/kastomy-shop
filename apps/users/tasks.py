from celery import shared_task
from django.core.mail import send_mail
from apps.users.sms_view import send_sms
from decouple import config


@shared_task
def send_otp_email_task(email, otp):
    send_mail(
        "Verification Code",
        f"Your Verify Code Is {otp}",
        str(config("EMAIL_STORE")),
        [email],
        fail_silently=False,
    )


@shared_task
def send_otp_sms_task(phone_number, code):
    send_sms(phone_number, f"Your verify code is {code}")
    return f"SMS sent to {phone_number}"
