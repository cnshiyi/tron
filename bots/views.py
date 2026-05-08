from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from .models import Bot, Promotion, BotGroup
from .serializers import BotSerializer, PromotionSerializer, BotGroupSerializer
from .services import TelegramBotService

class BotViewSet(viewsets.ModelViewSet):
    queryset = Bot.objects.all()
    serializer_class = BotSerializer
    search_fields = ["robot_id", "username", "first_name"]

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
