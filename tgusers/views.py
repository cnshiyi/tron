from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import TgUser, UserTop
from .serializers import TgUserSerializer, UserTopSerializer

class TgUserViewSet(viewsets.ModelViewSet):
    queryset = TgUser.objects.all().order_by("-is_top", "-id")
    serializer_class = TgUserSerializer
    filterset_fields = ["bot_id", "is_blacklisted", "is_top", "member_level"]
    search_fields = ["user_id", "username", "first_name", "inviter_id"]

    def _set_flag(self, field: str, value: bool):
        setattr(self.get_object(), field, value)
        user = self.get_object()
        setattr(user, field, value)
        user.save(update_fields=[field, "updated_at"])
        return Response(self.get_serializer(user).data)

    @action(detail=True, methods=["post"], url_path="blacklist")
    def blacklist(self, request, pk=None):
        return self._set_flag("is_blacklisted", True)

    @action(detail=True, methods=["post"], url_path="unblacklist")
    def unblacklist(self, request, pk=None):
        return self._set_flag("is_blacklisted", False)

    @action(detail=True, methods=["post"], url_path="top")
    def top(self, request, pk=None):
        return self._set_flag("is_top", True)

    @action(detail=True, methods=["post"], url_path="untop")
    def untop(self, request, pk=None):
        return self._set_flag("is_top", False)

class UserTopViewSet(viewsets.ModelViewSet):
    queryset = UserTop.objects.all().order_by("rank", "-id")
    serializer_class = UserTopSerializer
    filterset_fields = ["bot_id", "user_id", "rank_type"]
    search_fields = ["user_id"]
