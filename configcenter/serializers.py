from rest_framework import serializers

from .models import TextConfig


class TextConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextConfig
        fields = [
            "id",
            "key",
            "label",
            "value",
            "default_value",
            "category",
            "description",
            "sort",
            "is_active",
            "remark",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
