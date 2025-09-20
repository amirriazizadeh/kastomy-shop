from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from .serializers import (RegisterSerializer,RegisterSuccessSerializer,OTPRequestSerializer,
                           UserProfileSerializer,VerifyOTPSerializer,AddressSerializer,StoreRegistrationSerializer)
from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework.views import APIView
from .utils import generate_otp,verify_otp
from utils import send_otp_code,send_otp_code_by_email
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from stores.models import Store
from rest_framework_simplejwt.tokens import RefreshToken


User = get_user_model()

class RegisterView(generics.CreateAPIView):
    """
    This View provides an API endpoint for registering new users.
    This class inherits from GenericAPIView to easily implement the Create operation.
    """
    queryset = User.objects.all()
    permission_classes = (AllowAny,) # به همه کاربران (حتی احراز هویت نشده) اجازه دسترسی می‌دهد
    serializer_class = RegisterSerializer

    @extend_schema(
        summary="Register a new user account",
        description="""
        Create a new user by providing a username, email, and password.
        The password must be confirmed in the `password2` field.
        """,
        request=RegisterSerializer,
        responses={
            201: RegisterSuccessSerializer,
            400: {
                "description": "Bad Request: Occurs when validation fails (e.g., passwords don't match, username/email taken)."
            },
        },
        examples=[
            OpenApiExample(
                'Successful Registration Example',
                summary='A sample request to create a new user.',
                description='Provide all required fields to register a user named "johnsnow".',
                value={
                    "username": "johnsnow",
                    "email": "john.snow@example.com",
                    "password": "YouKnowNothing123!",
                    "password2": "YouKnowNothing123!"
                },
                request_only=True,    )
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
                "message": "User Created Successfully. Now perform Login to get your token.",
            },
            status=status.HTTP_201_CREATED
        )


class RequestOTPView(APIView):
    """
    API view to request a new OTP for an inactive user.
    Receives a username and sends a new OTP.
    """
    serializer_class = OTPRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data['phone_number']
        
        user = get_object_or_404(User, phone_number=phone_number)

        if user.is_active:
            return Response({"error": "This user is already active."}, status=status.HTTP_400_BAD_REQUEST)

        # Generate and send a new OTP
        otp = generate_otp(phone_number)
        send_otp_code(phone_number, otp)
        send_otp_code_by_email(user.email,otp)
        return Response({
            "seccses":"OTP has been sent seccesfully",
            "message": "A new verification code has been sent.",
            'expire_at':'2 minents'
            }, status=status.HTTP_200_OK)



class VerifyOTPView(APIView):
    """
    API view to verify OTP and activate the user account.
    """
    serializer_class = VerifyOTPSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        phone_number = serializer.validated_data['phone_number']
        otp_entered = serializer.validated_data['otp']
        
        user = get_object_or_404(User, phone_number=phone_number)
        
        if user.is_active:
            return Response({"error": "This account is already active."}, status=status.HTTP_400_BAD_REQUEST)
        
                
        # Retrieve OTP from cache
        is_verified = verify_otp(phone_number,otp_entered)

        if not is_verified:
            return Response({"error": "OTP is not valid."}, status=status.HTTP_400_BAD_REQUEST)

        # Activate user and clear OTP
        user.is_active = True
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
                "phone":user.phone_number,
                "is_seller":user.is_seller,
                "picture":user.profile_picture or "no picture",
                "address":addresses_list
            }
        }, status=status.HTTP_200_OK)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Manage the authenticated user's profile.
    Supports GET, PUT, PATCH, DELETE.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Retrieve and return the authenticated user.
        """
        return self.request.user
    




class AddressViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user addresses with logical delete.
    """
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return all addresses for the current user that are not deleted.
        """
        return self.request.user.addresses.filter(is_deleted=False)

    def perform_create(self, serializer):
        """
        Assign the current user to the address when creating a new one.
        """
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        """
        Perform a soft delete instead of a hard delete.
        """
        instance = self.get_object()
        instance.delete()  # Calls BaseModel.delete -> sets is_deleted=True
        return Response({"message":"deleted address seccesfully"},status=status.HTTP_204_NO_CONTENT)



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