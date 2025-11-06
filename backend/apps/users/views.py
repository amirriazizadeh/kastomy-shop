from apps.users.serializers import (
    UserReadSerializer,
    UserWriteSerializer,
    CodeSerializer,
    PasswordResetSerializer,
)
from rest_framework.response import Response
from rest_framework import status
from random import randint
from rest_framework.permissions import IsAuthenticated
from .signals import register_seller
from apps.users.tasks import send_otp_sms_task, send_otp_email_task
from django.core.cache import cache
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from django.conf import settings
from apps.users.permissions import IsSellerUser
from apps.stores.models import Store
from rest_framework_simplejwt.tokens import RefreshToken
import logging

logger = logging.getLogger(__name__)


class MyUserView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="My Profile",
        operation_description="see your profile",
        responses={200: UserReadSerializer, 401: "Unauthorized"},
        examples={
            "application/json": {
                "id": 1,
                "username": "john_doe",
                "email": "john@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "phone": "+989123456789",
                "is_seller": True,
                "date_joined": "2023-01-01T00:00:00Z",
            }
        },
    )
    def get(self, request):
        user = request.user
        if user.is_active:
            serializer = UserReadSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            {"message": "you are not active"}, status=status.HTTP_400_BAD_REQUEST
        )

    @swagger_auto_schema(
        request_body=UserWriteSerializer,
        operation_summary="Update Your Profile",
        operation_description="update your profile by changing all details",
        responses={200: UserReadSerializer, 400: "Bad Request", 401: "Unauthorized"},
        examples={
            "application/json": {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "phone": "+989123456789",
            }
        },
    )
    def put(self, request):
        user = request.user
        serializer = UserWriteSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=UserWriteSerializer,
        operation_summary="Update Your Profile",
        operation_description="update your profile by changing one detail",
        responses={200: UserReadSerializer, 400: "Bad Request", 401: "Unauthorized"},
        examples={"application/json": {"first_name": "Johnny"}},
    )
    def patch(self, request):
        user = request.user
        serializer = UserWriteSerializer(
            user,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Delete Your Profile",
        operation_description="delete your profile",
        responses={204: "No Content", 401: "Unauthorized"},
    )
    def delete(self, request):
        user = request.user
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception:
            pass
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SellerRegistrationView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=CodeSerializer,
        operation_summary="Register As Seller",
        operation_description="without code, otp will send - with code otp will verify",
        responses={
            200: "OTP sent or verification successful",
            400: "Bad Request - Already seller or invalid code",
            401: "Unauthorized",
        },
        examples={
            "application/json (send OTP)": {},
            "application/json (verify OTP)": {"code": "123456"},
        },
    )
    def post(self, request):
        user = request.user
        seller_otp_key = f"seller_otp_user_{user.id}"

        if "code" in request.data:
            serializer = CodeSerializer(data=request.data)
            if serializer.is_valid():
                user_otp = serializer.validated_data["code"]  # type: ignore
                main_otp = cache.get(seller_otp_key)
                if user_otp != main_otp:
                    return Response(
                        {"detail": "The entered code is incorrect."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                user.is_seller = True
                user.save()
                register_seller.send(sender=self.__class__, user=user)
                cache.delete(seller_otp_key)
                return Response(
                    {"message": "Congratulations! You are now a seller."},
                    status=status.HTTP_200_OK,
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        else:
            if user.is_seller:
                return Response(
                    {"message": "You are already a seller."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            code = randint(100000, 999999)
            cache.set(seller_otp_key, code, timeout=settings.OTP_TIME)
            logger.debug("Seller OTP for user %s: %s", user.id, code)
            send_otp_sms_task.delay(user.phone, code)
            send_otp_email_task.delay(user.email, code)
            return Response(
                {"message": "Verification code has been sent"},
                status=status.HTTP_200_OK,
            )


class DeleteRegistration(APIView):
    permission_classes = [IsSellerUser]

    @swagger_auto_schema(
        operation_summary="Delete Your Seller Registration",
        operation_description="delete your seller registration",
        responses={
            200: "Seller registration deleted successfully",
            401: "Unauthorized",
            403: "Forbidden - Not a seller",
        },
        examples={
            "application/json": {"message": "Seller registration deleted successfully"}
        },
    )
    def post(self, request):
        user = request.user
        user.is_seller = False
        user_store = Store.objects.filter(seller=user).first()
        if user_store:
            user_store.delete()
        user.save()
        return Response(
            {"message": "Seller registration deleted successfully"},
            status=status.HTTP_200_OK,
        )


class ResetPassword(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=PasswordResetSerializer,
        operation_summary="Change Your Password",
        operation_description="change your password",
        responses={
            200: "Password reset successful",
            400: "Bad Request - Validation errors",
            401: "Unauthorized",
        },
        examples={
            "application/json": {
                "old_password": "oldPassword123",
                "pass1": "newPassword456",
                "pass2": "newPassword456",
            }
        },
    )
    def post(self, request):
        user = request.user
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            old_password = data.get("old_password")  # type: ignore
            new_password = data.get("pass1")  # type: ignore
            confirm_password = data.get("pass2")  # type: ignore
            if not user.check_password(old_password):
                return Response(
                    {"error": "Old password is incorrect."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if new_password != confirm_password:
                return Response(
                    {"error": "New password and confirmation do not match."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if user.check_password(new_password):
                return Response(
                    {"error": "New password must be different from current password."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user.set_password(new_password)
            user.save()
            return Response(
                {"message": "Password has been reset successfully."},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
