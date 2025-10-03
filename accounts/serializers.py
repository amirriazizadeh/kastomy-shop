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

    def validate(self, attrs):
        # self.instance is the object being updated. It is None on create.
        # self.initial_data is the raw incoming data from the request.
        if self.instance and 'phone_number' in self.initial_data:
            raise serializers.ValidationError({'phone_number': 'شماره تلفن قابل تغییر نیست.'})
        return attrs
    
class AddressSerializer(serializers.ModelSerializer):
    """
    Serializer for the Address object
    """
    class Meta:
        model = Address
        fields = "__all__"
        read_only_fields = ('id', 'user','is_deleted','is_main')
    

class StoreRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer to create a store and upgrade the user to a seller.
    """
    address = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all(),
        write_only=True,
        label="انتخاب آدرس"
    )

    class Meta:
        model = Store
        fields = ['name', 'description', 'address']

    def __init__(self, *args, **kwargs):
        """
        Dynamically filter the address queryset to only show addresses
        belonging to the currently authenticated user.
        """
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            self.fields['address'].queryset = Address.objects.filter(user=request.user)

    def validate(self, data):
        """
        Check if the user already owns a store.
        """
        address = data.get('address')
        if address and address.is_deleted:
            raise serializers.ValidationError({"address": "این آدرس حذف شده است و نمی‌توان از آن استفاده کرد."})

        request_user = self.context['request'].user
        if Store.objects.filter(owner=request_user).exists():
             raise serializers.ValidationError("This user already has a store.")
        return data

    def create(self, validated_data):
        """
        Create the store, link the address, and upgrade the user to a seller.
        """
        request_user = self.context['request'].user
        
        try:
            with transaction.atomic():
                store = Store.objects.create(owner=request_user, **validated_data)
                
                if hasattr(request_user, 'is_seller'):
                    request_user.is_seller = True
                    request_user.save(update_fields=['is_seller'])
                    
                return store
        except Exception as e:
            raise serializers.ValidationError(str(e))


class LogoutInputSerializer(serializers.Serializer):
    """ورودی برای خروج کاربر"""
    refresh = serializers.CharField(
        help_text="Refresh token کاربر که باید بلاک شود."
    )