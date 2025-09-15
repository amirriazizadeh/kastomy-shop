from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from .serializers import (RegisterSerializer,RegisterSuccessSerializer,OTPRequestSerializer,
                           UserProfileSerializer,VerifyOTPSerializer,AddressSerializer)
from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework.views import APIView
from .utils import generate_otp,verify_otp
from utils import send_otp_code
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets

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
    API view to generate and send (print to terminal) an OTP.
    """
    def post(self, request, *args, **kwargs):
        serializer = OTPRequestSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone_number']
            
            try:
                User.objects.get(phone_number=phone, is_active=False)
            except User.DoesNotExist:
                return Response({"error": "User with this phone number is not registered or is already active."}, status=status.HTTP_404_NOT_FOUND)


            # Store OTP in cache with a 2-minute timeout
            otp = generate_otp(phone)
            send_otp_code(phone, otp)
            
            return Response({"message": "OTP has been sent successfully."}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):
    """
    API view to verify the submitted OTP and activate the user.
    """
    def post(self, request, *args, **kwargs):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            submitted_otp = serializer.validated_data['otp']
            
            # Retrieve OTP from cache
            is_verified = verify_otp(phone_number,submitted_otp)
            
            if not is_verified:
                return Response({"error": "OTP is not valid."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                user = User.objects.get(phone_number=phone_number)
                if user.is_active:
                    return Response({"message": "User is already active."}, status=status.HTTP_400_BAD_REQUEST)
                
                # Activate the user
                user.is_active = True
                user.save()
                

                return Response({
                    "message": "Account verified successfully. You can now log in."
                    # "tokens": tokens 
                }, status=status.HTTP_200_OK)

            except User.DoesNotExist:
                return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UserProfileView(generics.RetrieveUpdateDestroyAPIView):
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
    ViewSet for managing user addresses.
    Provides list, create, retrieve, update, and destroy actions.
    """
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        This view should return a list of all the addresses
        for the currently authenticated user.
        """
        return self.request.user.addresses.all()

    def perform_create(self, serializer):
        """
        Assign the current user to the address when creating a new one.
        """
        serializer.save(user=self.request.user)