# from kavenegar import *
# from decouple import config


# def send_otp_code(phone_number, code):
# 	params = {
# 		'sender': '2000660110',
# 		'receptor': phone_number,
# 		'message': f'{code} کد تایید شما '
# 	}
# 	try:
# 		api = KavenegarAPI(config('api'))
# 		response = api.sms_send(params)
# 		print(response)
# 	except APIException as e:
# 		print(e)
# 	except HTTPException as e:
# 		print(e)

def send_otp_code(phone_number, code):

	print(f'otp code for: {phone_number} --- is:  ')



from django.core.mail import send_mail
from django.conf import settings

def send_otp_code_by_email(email,code):
    subject = "Verify Code Email"
    message = f"your validation code is: {code}"
    recipient_list = [email,]  
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
    print(code)
