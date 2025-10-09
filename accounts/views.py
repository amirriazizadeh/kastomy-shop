from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model

from accounts.models import Address
from .serializers import (RegisterSerializer,RegisterSuccessSerializer,OTPRequestSerializer,
                         UserProfileSerializer,VerifyOTPSerializer,AddressSerializer,
                         StoreRegistrationSerializer,LogoutInputSerializer)
from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework.views import APIView
from .utils import generate_otp,verify_otp
from utils import send_otp_code
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from stores.models import Store
from rest_framework_simplejwt.tokens import RefreshToken
from .tasks import send_otp_code_by_email
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

User = get_user_model()



class RegisterView(generics.CreateAPIView):
    """
    ثبت‌نام کاربر جدید.

    توضیحات:
        - این ویو یک حساب کاربری جدید ایجاد می‌کند.  
        - کاربر باید نام کاربری، ایمیل و رمز عبور را وارد کند.  
        - رمز عبور باید دوبار (password, password2) وارد شود تا مطمئن شویم درست تایپ شده.  
    """
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    @extend_schema(
        summary="ثبت‌نام کاربر جدید",
        description="""
        کاربر جدید را با ارسال `username`, `email`, `password` و `password2` ایجاد می‌کند.  
        در صورت موفقیت، اطلاعات کاربر جدید و یک پیام راهنما برمی‌گردد.  
        در صورت خطا، پیام خطا شامل جزئیات اعتبارسنجی خواهد بود.
        """,
        request=RegisterSerializer,
        responses={
            201: RegisterSuccessSerializer,
            400: {
                "description": "خطا در اعتبارسنجی (مثلاً: عدم تطابق پسوردها، تکراری بودن username/email)."
            },
        },
        examples=[
            OpenApiExample(
                'نمونه ثبت‌نام موفق',
                summary='درخواست نمونه برای ساخت کاربر',
                description='ایجاد کاربر با نام "johnsnow"',
                value={
                    "username": "johnsnow",
                    "email": "john.snow@example.com",
                    "password": "YouKnowNothing123!",
                    "password2": "YouKnowNothing123!"
                },
                request_only=True
            )
        ],
        tags=['Authentication']
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "user": serializer.data,
                "message": "کاربر با موفقیت ساخته شد. برای ورود از لاگین استفاده کنید.",
            },
            status=status.HTTP_201_CREATED
        )



class RequestOTPView(APIView):
    """
    view API برای درخواست یک رمز یکبار مصرف جدید برای یک کاربر غیرفعال.
      یک نام کاربری دریافت کرده و یک رمز یکبار مصرف جدید ارسال می‌کند.
    """
    serializer_class = OTPRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        
        user = get_object_or_404(User, username=username)

        if user.is_active=="active":
            return Response({"error": "This user is already active."}, status=status.HTTP_400_BAD_REQUEST)

        otp = generate_otp(user.phone)
        send_otp_code(user.phone, otp)
        send_otp_code_by_email.delay(user.email,otp)
        return Response({
            "seccses":"OTP has been sent seccesfully",
            "message": "A new verification code has been sent.",
            'expire_at':'2 minents'
            }, status=status.HTTP_200_OK)



class VerifyOTPView(APIView):
    
    serializer_class = VerifyOTPSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        username = serializer.validated_data['username']
        otp_entered = serializer.validated_data['password']
        
        user = get_object_or_404(User, username=username)
        
        if user.is_active=="active":
            return Response({"error": "This account is already active."}, status=status.HTTP_400_BAD_REQUEST)
        
                
        # Retrieve OTP from cache
        is_verified = verify_otp(user.phone,otp_entered)

        if not is_verified:
            return Response({"error": "OTP is not valid."}, status=status.HTTP_400_BAD_REQUEST)

        # Activate user and clear OTP
        user.is_active = "True"
        user.save()

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        addresses_list = [
        {
        "id": address.id,
        "label": address.label,
        "address_line_1": address.address_line_1,
        "address_line_2": address.address_line_2,
        "city": address.city,
        "state": address.state,
        "postal_code": address.postal_code,
        "country": address.country,
        # Note: Datetime fields should ideally be serialized to a string format
        # DRF serializers do this automatically, but here we can just pass them.
        "created_at": address.created_at,
        "updated_at": address.updated_at,
        }
        for address in user.addresses.all() # We loop through all addresses here
        ]

        return Response({
            "access": str(access),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "email":user.email,
                "first_name":user.first_name,
                "last_name":user.last_name,
                "phone":user.phone,
                "is_seller":user.is_seller,
                "picture":user.picture or "no picture",
                "address":addresses_list
            }
        }, status=status.HTTP_200_OK)




class LogoutView(APIView):
    """
    خروج کاربر (Logout).

    آدرس:
        `/api/logout/`

    توضیحات:
        - کاربر باید **refresh token** معتبر خود را در body ارسال کند.  
        - این توکن در blacklist قرار می‌گیرد و دیگر قابل استفاده نخواهد بود.  
        - در صورت موفقیت، وضعیت `205 RESET CONTENT` برگردانده می‌شود.  
    """
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        summary="خروج کاربر",
        description="این متد refresh token کاربر را بلاک می‌کند تا دیگر قابل استفاده نباشد.",
        request=LogoutInputSerializer,
        responses={
            205: None,
            400: dict
        }
    )
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message":"You loged out seccessfuly..."},status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({"detail": "توکن نامعتبر یا قبلاً بلاک شده است."},
                            status=status.HTTP_400_BAD_REQUEST)





class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request, *args, **kwargs):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=True  
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)







class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user, is_deleted=False)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        print(serializer.errors)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.save()
        return Response({"message": "Address deleted successfully"}, status=status.HTTP_204_NO_CONTENT)




class SellerRegistrationAPIView(generics.CreateAPIView):
    """
    API endpoint for a customer to register as a seller by creating a store.
    """
    serializer_class = StoreRegistrationSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context