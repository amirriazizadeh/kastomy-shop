from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from .models import CustomUser
from stores.models import Store
from .models import CustomUser, Address


User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    """
    سریالایزر برای ثبت‌نام کاربران جدید با استفاده از نام کاربری، شماره تلفن و ایمیل.
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
        
        fields = [ 'phone_number', 'email', 'password', 'password2']
        

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        attrs.pop('password2')
        return attrs

    def create(self, validated_data):
        """
        متد create برای ساخت کاربر جدید با استفاده از create_user.
        """
        user = User.objects.create_user(
            phone_number=validated_data['phone_number'],
            email=validated_data['email'],
            password=validated_data['password'],
            # اگر نقش مشخص نشود، به صورت پیش‌فرض مشتری در نظر گرفته می‌شود
            role=validated_data.get('role', User.Role.CUSTOMER) 
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    سریالایزر برای نمایش اطلاعات کاربر.
    در پاسخ ثبت‌نام موفق استفاده می‌شود.
    """
    class Meta:
        model = User
        # فیلدهای بیشتری برای نمایش اطلاعات کامل‌تر کاربر اضافه شد
        fields = ('id', 'phone_number', 'email', 'role')


class RegisterSuccessSerializer(serializers.Serializer):
    """
    این سریالایزر صرفا برای مستندسازی خروجی در Swagger/OpenAPI استفاده می‌شود.
    """
    user = UserSerializer()
    message = serializers.CharField(default="User registered successfully.")


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
        fields = "__all__"
        read_only_fields = ('id', 'user')




class StoreRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer to create a store and upgrade the user to a seller.
    """
    class Meta:
        model = Store
        fields = ['name', 'description']

    def create(self, validated_data):
        request_user = self.context['request'].user

        if request_user.is_seller:
            raise serializers.ValidationError("This user is already a seller and cannot create a new store.")

        try:
            with transaction.atomic():
                validated_data['owner'] = request_user
                store = Store.objects.create(**validated_data)
                request_user.is_seller = True
                request_user.save(update_fields=['is_seller'])
                return store
        except Exception as e:
            raise serializers.ValidationError(str(e))