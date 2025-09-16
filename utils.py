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

	print(f'otp code for: {phone_number} --- is:  {code}')

# send_otp_code('09184222500','2345')