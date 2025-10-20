from rest_framework import serializers
from apps.categories.models import Category


class CategorySimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "parent"]


class CategoryReadSerializer(serializers.ModelSerializer):
    children = CategorySimpleSerializer(many=True, read_only=True)
    parents = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "description",
            "image",
            "is_active",
            "parents",
            "children",
        ]
        read_only_fields = fields

    def get_parents(self, obj):
        parents = []
        current = obj.parent
        while current:
            parents.insert(0, CategorySimpleSerializer(current).data)
            current = current.parent
        return parents


class CategoryWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["name", "description", "image", "parent", "is_active"]
        extra_kwargs = {
            "parent": {"required": False, "allow_null": True},
            "is_active": {"required": False},
        }
