from rest_framework import viewsets
from .models import TgUser, UserTop
from .serializers import TgUserSerializer, UserTopSerializer

class TgUserViewSet(viewsets.ModelViewSet):
    queryset = TgUser.objects.all()
    serializer_class = TgUserSerializer
    filterset_fields = ["bot_id", "is_blacklisted", "is_top", "member_level"]
    search_fields = ["user_id", "username", "first_name", "inviter_id"]

class UserTopViewSet(viewsets.ModelViewSet):
    queryset = UserTop.objects.all()
    serializer_class = UserTopSerializer
    filterset_fields = ["bot_id", "user_id", "rank_type"]
    search_fields = ["user_id"]
