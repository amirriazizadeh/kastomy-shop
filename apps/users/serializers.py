
from rest_framework import serializers
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model


User = get_user_model()




class UserWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "email",
            "phone",
            "password",
            "first_name",
            "last_name",
            "picture",
        ]
        extra_kwargs = {
            "password": {"write_only": True, "required": False},
            "picture": {"allow_null": True, "required": False},
        }

    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError("required email")

        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError("please enter a correct email")

        if self.instance:
            if User.objects.filter(email=value).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError(
                    "this email is used, choose another one"
                )
        else:
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError("this email has been used before")

        return value.lower()

    def validate_phone(self, value):
        if not value:
            return value

        ir_phone_pattern = r"^(\+98|0)?9\d{9}$"
        if not re.match(ir_phone_pattern, value):
            raise serializers.ValidationError("please enter a correct iranian number")
        if value.startswith("+98"):
            value = "0" + value[3:]

        if self.instance:
            if User.objects.filter(phone=value).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("this phone has been used before")
        else:
            if User.objects.filter(phone=value).exists():
                raise serializers.ValidationError("this phone has been used before")

        return value

    def validate_password(self, value):
        if self.instance and value:
            raise serializers.ValidationError(
                "Cannot update password using this endpoint."
            )
        if not value:
            raise serializers.ValidationError("required password")
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)

        return value

    def validate_first_name(self, value):
        if value and len(value.strip()) < 2:
            raise serializers.ValidationError("first name must be 2 character at least")

        if value and not all(c.isalpha() or c.isspace() for c in value):
            raise serializers.ValidationError(
                "first name must contain only letter and space"
            )

        return value.strip() if value else value

    def validate_last_name(self, value):
        if value and len(value.strip()) < 2:
            raise serializers.ValidationError("last name must be 2 character at least")

        if value and not all(c.isalpha() or c.isspace() for c in value):
            raise serializers.ValidationError(
                "last name must contain only letter and space"
            )

        return value.strip() if value else value

    def validate(self, data):
        if not data.get("first_name") and not data.get("last_name"):
            raise serializers.ValidationError(
                {"non_field_errors": ["enter first or last name at least"]}
            )

        if self.instance is None and not data.get("password"):
            raise serializers.ValidationError({"password": ["password is required"]})

        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            phone=validated_data.get("phone"),
            password=validated_data["password"],
            picture=validated_data.get("picture"),
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )  # type: ignore
        return user
