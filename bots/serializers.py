from rest_framework import serializers
from .models import Bot, Promotion, BotGroup, BroadcastLog

class BotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bot
        fields = "__all__"

class PromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = "__all__"

class BotGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = BotGroup
        fields = "__all__"



class BotBulkCreateSerializer(serializers.Serializer):
    """Accept one bot per line for batch creation.

    Supported formats:
    - token
    - robot_id,token
    - robot_id|token|username|first_name|owner_user_id
    """

    content = serializers.CharField(allow_blank=False, trim_whitespace=True)
    default_owner_user_id = serializers.CharField(required=False, allow_blank=True, default="")
    webhook_enabled = serializers.BooleanField(required=False, default=True)
    broadcast_enabled = serializers.BooleanField(required=False, default=True)



class BroadcastLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = BroadcastLog
        fields = "__all__"

class BotBroadcastSerializer(serializers.Serializer):
    content = serializers.CharField(allow_blank=False, trim_whitespace=True)
    title = serializers.CharField(required=False, allow_blank=True, default="")
    chat_id = serializers.CharField(required=False, allow_blank=True, default="")
    dry_run = serializers.BooleanField(required=False, default=True)

class BotWebhookSerializer(serializers.Serializer):
    base_url = serializers.URLField(required=False, allow_blank=True, default="")
    drop_pending_updates = serializers.BooleanField(required=False, default=True)
    dry_run = serializers.BooleanField(required=False, default=True)
