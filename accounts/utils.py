import redis
import random
from django.conf import settings

r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)
from django.core.cache import cache


def generate_otp(phone):
    """Generate and store OTP code in Redis for 2 minutes"""
    otp = str(random.randint(100000, 999999))
    # r.setex(f"otp:{phone}", 120, otp)
    cache.set(f"otp:{phone}",otp,120)
    return otp


def verify_otp(phone, otp):
    """Verify the OTP stored in Redis"""
    stored = cache.get(f"otp:{phone}")
    if stored == otp:
        cache.delete(f"otp:{phone}") 
        return True
    return False


def delete_otp():
    pass


