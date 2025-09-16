from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from .models import CustomUser
from stores.models import Store


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
        
        fields = ['username', 'phone_number', 'email', 'password', 'password2']
        

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
            username=validated_data['username'],
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
        fields = ('id', 'username', 'phone_number', 'email', 'role')


class RegisterSuccessSerializer(serializers.Serializer):
    """
    این سریالایزر صرفا برای مستندسازی خروجی در Swagger/OpenAPI استفاده می‌شود.
    """
    user = UserSerializer()
    message = serializers.CharField(default="User registered successfully.")


class OTPRequestSerializer(serializers.Serializer):
    """
    Serializer to request a new OTP. Takes username as input.
    """
    username = serializers.CharField(required=True)

class VerifyOTPSerializer(serializers.Serializer):
    """
    Serializer to verify the OTP and activate the user.
    """
    username = serializers.CharField(required=True)
    otp = serializers.CharField(required=True, max_length=6)

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
        fields = "__all__"
        read_only_fields = ('id', 'user')


class SellerUserSerializer(serializers.ModelSerializer):
    """
    Serializer specifically for creating a user with the 'SELLER' role.
    """
    
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ('phone_number', 'password', 'email', 'first_name', 'last_name')
        extra_kwargs = {
            'email': {'required': False, 'allow_blank': True},
            'first_name': {'required': False, 'allow_blank': True},
            'last_name': {'required': False, 'allow_blank': True},
        }

    def create(self, validated_data):

        user = CustomUser.objects.create_user(
            phone_number=validated_data['phone_number'],
            password=validated_data['password'],
            email=validated_data.get('email'),
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            role=CustomUser.Role.SELLER,
            is_active=False
        )
        return user


class StoreRegistrationSerializer(serializers.ModelSerializer):
    """
    Main serializer for registering a store.
    It includes nested user data for the owner.
    """
    owner = SellerUserSerializer()

    class Meta:
        model = Store
        fields = ('owner', 'name', 'description', 'address')

    def create(self, validated_data):
        # Pop the nested owner data
        owner_data = validated_data.pop('owner')
        
        # Use a database transaction to ensure atomicity.
        # This means if store creation fails, user creation is also rolled back.
        with transaction.atomic():
            # Create the user using the SellerUserSerializer
            owner_serializer = SellerUserSerializer(data=owner_data)
            owner_serializer.is_valid(raise_exception=True)
            owner = owner_serializer.save()

            # Create the store and link the owner
            # **owner is the user instance, validated_data contains store fields
            store = Store.objects.create(owner=owner, **validated_data)
        
        return store