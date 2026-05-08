from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Bot, Promotion, BotGroup
from .serializers import BotBulkCreateSerializer, BotSerializer, PromotionSerializer, BotGroupSerializer
from .services import TelegramBotService

class BotViewSet(viewsets.ModelViewSet):
    queryset = Bot.objects.all()
    serializer_class = BotSerializer
    search_fields = ["robot_id", "username", "first_name"]

    @action(detail=False, methods=["post"], url_path="bulk-create")
    def bulk_create(self, request):
        serializer = BotBulkCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        created = []
        skipped = []
        errors = []

        for line_no, raw_line in enumerate(data["content"].splitlines(), start=1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            delimiter = "|" if "|" in line else "," if "," in line else None
            parts = [part.strip() for part in line.split(delimiter)] if delimiter else [line]

            if len(parts) == 1:
                token = parts[0]
                robot_id = token.split(":", 1)[0] if ":" in token else token[:64]
                username = ""
                first_name = ""
                owner_user_id = data.get("default_owner_user_id", "")
            elif len(parts) >= 2:
                robot_id, token = parts[0], parts[1]
                username = parts[2] if len(parts) > 2 else ""
                first_name = parts[3] if len(parts) > 3 else ""
                owner_user_id = parts[4] if len(parts) > 4 else data.get("default_owner_user_id", "")
            else:
                errors.append({"line": line_no, "content": raw_line, "error": "格式错误"})
                continue

            if not robot_id or not token:
                errors.append({"line": line_no, "content": raw_line, "error": "robot_id/token 不能为空"})
                continue

            bot, was_created = Bot.objects.get_or_create(
                robot_id=robot_id,
                defaults={
                    "token": token,
                    "username": username,
                    "first_name": first_name,
                    "owner_user_id": owner_user_id,
                    "webhook_enabled": data.get("webhook_enabled", True),
                    "broadcast_enabled": data.get("broadcast_enabled", True),
                },
            )
            if was_created:
                created.append(BotSerializer(bot).data)
            else:
                skipped.append({"line": line_no, "robot_id": robot_id, "reason": "机器人ID已存在"})

        return Response(
            {"created": created, "created_count": len(created), "skipped": skipped, "errors": errors},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

class PromotionViewSet(viewsets.ModelViewSet):
    queryset = Promotion.objects.select_related("bot").all()
    serializer_class = PromotionSerializer
    filterset_fields = ["bot", "position", "type", "auto_reply"]
    search_fields = ["title", "command", "content"]

class BotGroupViewSet(viewsets.ModelViewSet):
    queryset = BotGroup.objects.select_related("bot").all()
    serializer_class = BotGroupSerializer
    filterset_fields = ["bot", "chat_id", "broadcast_enabled"]
    search_fields = ["chat_id", "title"]

@csrf_exempt
def telegram_webhook(request, bot_id: str):
    if request.method != "POST":
        return JsonResponse({"detail": "POST required"}, status=405)
    result = TelegramBotService().handle_webhook(bot_id, request.body)
    return JsonResponse(result)
