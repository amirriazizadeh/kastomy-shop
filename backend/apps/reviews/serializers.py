from rest_framework import serializers
from apps.reviews.models import Review
from apps.products.models import Product
from apps.stores.models import Store
from apps.users.serializers_base import UserSimpleSerializer
from apps.products.serializers import ProductReadSerializer
from apps.stores.serializers import StoreReadSerializer


class ReviewProductReadSerializer(serializers.ModelSerializer):
    user = UserSimpleSerializer(read_only=True)
    product = ProductReadSerializer(read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "user",
            "rating",
            "comment",
            "product",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class ReviewProductWriteSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), write_only=True
    )

    class Meta:
        model = Review
        fields = ["rating", "comment", "product_id"]

    def create(self, validated_data):
        user = self.context["request"].user
        product = validated_data.pop("product_id")
        if Review.objects.filter(product=product, user=user).exists():
            raise serializers.ValidationError("You have already reviewed this product.")
        return Review.objects.create(user=user, product=product, **validated_data)


class ReviewStoreReadSerializer(serializers.ModelSerializer):
    user = UserSimpleSerializer(read_only=True)
    store = StoreReadSerializer(read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "user",
            "rating",
            "comment",
            "store",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class ReviewStoreWriteSerializer(serializers.ModelSerializer):
    store_id = serializers.PrimaryKeyRelatedField(
        queryset=Store.objects.all(), write_only=True
    )

    class Meta:
        model = Review
        fields = ["rating", "comment", "store_id"]

    def create(self, validated_data):
        user = self.context["request"].user
        store = validated_data.pop("store_id")

        if Review.objects.filter(store=store, user=user).exists():
            raise serializers.ValidationError("You have already reviewed this store.")

        return Review.objects.create(user=user, store=store, **validated_data)
