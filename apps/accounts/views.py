from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from apps.users.serializers import UserWriteSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.conf import settings
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
)
from .serializers import (
    RefreshSerializer,
)

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

