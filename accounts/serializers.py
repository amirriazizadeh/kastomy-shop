from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

# دریافت مدل کاربر فعال پروژه
User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    """
    سریالایزر برای ثبت‌نام کاربران جدید.
    این سریالایزر شماره تلفن، ایمیل (اختیاری) و رمز عبور را دریافت کرده
    و پس از اعتبارسنجی، کاربر جدیدی ایجاد می‌کند.
    """
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True, 
        required=True, 
        label="Confirm password",
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        
        fields = ['phone_number', 'email', 'password', 'password2', 'role']
        extra_kwargs = {
            'email': {'required': False},
            'role': {'required': False} # نقش کاربر در هنگام ثبت‌نام اختیاری است
        }

    def validate(self, attrs):
        
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
                
        attrs.pop('password2')
        return attrs

    def create(self, validated_data):
        
        user = User.objects.create_user(
            phone_number=validated_data['phone_number'],
            password=validated_data['password'],
            email=validated_data.get('email'),
            role=validated_data.get('role', User.Role.CUSTOMER) # اگر نقش مشخص نشود، مشتری در نظر گرفته می‌شود
        )
        return user

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying basic user information safely.
    Used as a nested serializer in the registration success response.
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

class RegisterSuccessSerializer(serializers.Serializer):
    """
    Defines the schema for a successful registration response.
    This is used exclusively for documentation purposes in @extend_schema.
    """
    user = UserSerializer()
    message = serializers.CharField()

class OTPRequestSerializer(serializers.Serializer):
    """
    Serializer for requesting an OTP. Just needs the phone number.
    """
    phone_number = serializers.CharField(max_length=15)

class VerifyOTPSerializer(serializers.Serializer):
    """
    Serializer for verifying the OTP code.
    """
    phone_number = serializers.CharField(max_length=15)
    otp = serializers.CharField(max_length=6, write_only=True)

from .models import CustomUser, Address
class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for viewing and updating the authenticated user's profile.
    """
    profile_picture = serializers.ImageField(required=False, allow_null=True, use_url=True)

    class Meta:
        model = CustomUser
        fields = [
            'phone_number', 'first_name', 'last_name', 'email',
            'role', 'is_active', 'is_staff', 'profile_picture',
        ]
        read_only_fields = ('phone_number', 'role', 'is_active', 'is_staff')

class AddressSerializer(serializers.ModelSerializer):
    """
    Serializer for the Address object
    """
    class Meta:
        model = Address
        fields = ('id', 'user', 'province', 'city', 'street', 'postal_code')
        read_only_fields = ('id', 'user')

