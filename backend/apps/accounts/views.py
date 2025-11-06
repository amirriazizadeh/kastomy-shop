from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
from random import randint
from apps.users.tasks import send_otp_email_task
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.throttling import ScopedRateThrottle
from apps.users.serializers import UserWriteSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.conf import settings
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from apps.accounts.serializers import (
    OtpRequestSerializer,
    OtpVerifySerializer,
    RefreshSerializer,
)
from apps.users.models import User

TOKEN_RESPONSE = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "refresh": openapi.Schema(
            type=openapi.TYPE_STRING,
            example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY3ODgwNzk3OCwiaWF0IjoxNjc4NzIxNTc4LCJqdGkiOiJkZDhmMTYyMjFiNTA0Y2ZjOGQxZWE2NjkwYzQ0YTY1ZSIsInVzZXJfaWQiOjF9",
        ),
        "access": openapi.Schema(
            type=openapi.TYPE_STRING,
            example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjc4NzIyNDc4LCJpYXQiOjE2Nzg3MjE1NzgsImp0aSI6ImIxNWI3ZTFmMDVkOTRiOGY5MTI2YWMxNjE0NTVjYTljIiwidXNlcl9pZCI6MX0",
        ),
    },
    required=["refresh", "access"],
)

MESSAGE_RESPONSE = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "message": openapi.Schema(
            type=openapi.TYPE_STRING, example="A message response."
        ),
    },
)


class TokenObtainPairViewSwagger(TokenObtainPairView):
    @swagger_auto_schema(
        operation_summary="Log In",
        operation_description="enter your phone and password",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "phone": openapi.Schema(
                    type=openapi.TYPE_STRING, example="09123456789"
                ),
                "password": openapi.Schema(
                    type=openapi.TYPE_STRING, example="yourpassword"
                ),
            },
            required=["phone", "password"],
        ),
        responses={
            200: openapi.Response(
                description="Token pair generated successfully", schema=TOKEN_RESPONSE
            ),
        },
    )
    def post(self, request: Request, *args, **kwargs) -> Response:
        return super().post(request, *args, **kwargs)



class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=RefreshSerializer,
        operation_summary="Log Out",
        operation_description="Enter your refresh token",
        responses={
            200: openapi.Response(
                description="Successfully logged out",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING, example="Successfully logged out"
                        )
                    },
                ),
            ),
            400: "Bad Request (Serializer Error)",
            401: openapi.Response(
                description="Invalid Token",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="Token is invalid or expired",
                        )
                    },
                ),
            ),
        },
    )
    def post(self, request):
        serializer = RefreshSerializer(data=request.data)
        if serializer.is_valid():
            refresh_token = serializer.validated_data["refresh"]  # type: ignore
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
                return Response(
                    {"message": "Successfully logged out"}, status=status.HTTP_200_OK
                )
            except TokenError as e:
                return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Register(APIView):
    permission_classes = [AllowAny]

    USER_WRITE_RESPONSE = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "id": openapi.Schema(type=openapi.TYPE_INTEGER, example=2),
            "email": openapi.Schema(
                type=openapi.TYPE_STRING, example="newuser@example.com"
            ),
            "phone": openapi.Schema(type=openapi.TYPE_STRING, example="09123456789"),
            "first_name": openapi.Schema(type=openapi.TYPE_STRING, example="John"),
            "last_name": openapi.Schema(type=openapi.TYPE_STRING, example="Doe"),
            "picture": openapi.Schema(
                type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, example=None
            ),
        },
    )

    @swagger_auto_schema(
        request_body=UserWriteSerializer,
        operation_summary="Registration",
        operation_description="register by your information (picture is optional)",
        responses={
            201: openapi.Response(
                description="User successfully created", schema=USER_WRITE_RESPONSE
            ),
            400: openapi.Response(
                description="Validation error (e.g., duplicate email/phone)",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "email": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(type=openapi.TYPE_STRING),
                            example=["user with this email already exists."],
                        )
                    },
                ),
            ),
        },
    )
    def post(self, request):
        serializer = UserWriteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenRefreshViewSwagger(TokenRefreshView):
    @swagger_auto_schema(
        operation_summary="Verify Refresh Token",
        operation_description="enter your refresh token",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "refresh": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY3ODgwNzk3OCwiaWF0IjoxNjc4NzIxNTc4LCJqdGkiOiJkZDhmMTYyMjFiNTA0Y2ZjOGQxZWE2NjkwYzQ0YTY1ZSIsInVzZXJfaWQiOjF9",
                ),
            },
            required=["refresh"],
        ),
        responses={
            200: openapi.Response(
                description="New access token generated",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "access": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjc4NzIyNjYxLCJpYXQiOjE2Nzg3MjE3NjEsImp0aSI6ImUyNTdjZWY3MTA2NjRiMmNhM2IyY2IyODQ4ZDFjY2QwIiwidXNlcl9pZCI6MX0",
                        ),
                    },
                    required=["access"],
                ),
            ),
        },
    )
    def post(self, request: Request, *args, **kwargs) -> Response:
        return super().post(request, *args, **kwargs)



class RequestOtp(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "otp_request"

    @swagger_auto_schema(
        request_body=OtpRequestSerializer,
        operation_summary="Request Otp By Email",
        operation_description="enter your email",
        responses={
            200: openapi.Response(
                description="OTP successfully sent",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="An OTP has been sent to your email.",
                        )
                    },
                ),
            ),
            400: "Bad Request",
        },
    )
    def post(self, request):
        serializer = OtpRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]  # type: ignore
            otp_key = f"otp_{email}"
            otp = cache.get(otp_key)
            if not otp:
                otp = randint(1000, 9999)
                cache.set(otp_key, otp, timeout=settings.OTP_TIME)
            print(otp)  # for testing purposes
            send_otp_email_task.delay(email, otp)
            return Response(
                {"message": "An OTP has been sent to your email."},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }

class VerifyOtp(APIView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "otp_verify"
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=OtpVerifySerializer,
        operation_summary="Verify Otp",
        operation_description="check your email and enter code and your email again",
        responses={
            200: openapi.Response(
                description="Token generation success", schema=TOKEN_RESPONSE
            ),
            400: openapi.Response(
                description="Invalid or expired OTP / Incorrect OTP",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="The provided OTP is incorrect.",
                        ),
                        "message_expired": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="OTP has expired or is invalid.",
                        ),
                    },
                ),
            ),
            404: openapi.Response(
                description="User not found",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING, example="User not found."
                        )
                    },
                ),
            ),
        },
    )
    def post(self, request):
        serializer = OtpVerifySerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]  # type: ignore
            sent_otp = serializer.validated_data["otp"]  # type: ignore
            otp_key = f"otp_{email}"
            main_otp = cache.get(otp_key)
            if main_otp is None:
                return Response(
                    {"message": "OTP has expired or is invalid."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if sent_otp == main_otp:
                try:
                    user = User.objects.get(email=email)
                    cache.delete(otp_key)
                    tokens = get_tokens_for_user(user)
                    return Response(tokens, status=status.HTTP_200_OK)
                except User.DoesNotExist:
                    return Response(
                        {"message": "User not found."}, status=status.HTTP_404_NOT_FOUND
                    )
            else:
                return Response(
                    {"message": "The provided OTP is incorrect."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
