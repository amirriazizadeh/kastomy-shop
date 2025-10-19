from kavenegar import KavenegarAPI, APIException, HTTPException
from decouple import config


def send_sms(to_number, message):
    api = KavenegarAPI(config("KAVENEGAR_API"))
    try:
        response = api.sms_send(
            sender="2000660110",  # type: ignore
            receptor=to_number,  # type: ignore
            message=message,  # type: ignore
        )
        return response
    except APIException as e:
        print(f"API Exception: {e}")
        return None
    except HTTPException as e:
        print(f"HTTP Exception: {e}")
        return None
