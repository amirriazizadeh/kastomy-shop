from rest_framework import serializers


class OtpRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class OtpVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.IntegerField()


class RefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()
