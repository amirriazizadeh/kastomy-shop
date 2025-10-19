




from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

from time import sleep

@shared_task
def send_otp_code_by_email(email,code):
    
    subject = "Verify Code Email"
    message = f"your validation code is: {code}"
    recipient_list = [email,]  
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
    print(code)






