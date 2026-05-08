from rest_framework import serializers
from .models import TgUser, UserTop

class TgUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TgUser
        fields = "__all__"

class UserTopSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTop
        fields = "__all__"
