from rest_framework import serializers
from apps.addresses.models import Address


class AddressWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ["label", "city", "state", "postal_code", "country", "is_default"]

    def create(self, validated_data):
        user = self.context["request"].user
        is_default = validated_data.get("is_default", False)
        if is_default:
            Address.objects.filter(user=user, is_default=True).update(is_default=False)
        address = Address.objects.create(user=user, **validated_data)
        return address

    def update(self, instance, validated_data):
        is_default = validated_data.get("is_default", False)
        if is_default:
            Address.objects.filter(user=instance.user, is_default=True).exclude(
                id=instance.id
            ).update(is_default=False)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class AddressReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            "id",
            "label",
            "city",
            "state",
            "postal_code",
            "country",
            "is_default",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields
