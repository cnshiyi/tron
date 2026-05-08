from rest_framework import serializers
from .models import Bot, Promotion, BotGroup

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

