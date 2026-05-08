import json
from .models import Bot, Promotion

class TelegramBotService:
    def handle_webhook(self, bot_id: str, raw_body: bytes) -> dict:
        try:
            update = json.loads(raw_body.decode("utf-8"))
        except Exception as exc:
            return {"ok": False, "error": f"invalid json: {exc}"}
        bot = Bot.objects.filter(robot_id=bot_id, is_active=True).first()
        if not bot:
            return {"ok": False, "error": "bot not found"}
        message = update.get("message") or update.get("callback_query", {}).get("message") or {}
        text = message.get("text") or update.get("callback_query", {}).get("data") or ""
        replies = list(Promotion.objects.filter(bot=bot, is_active=True, auto_reply=True, command=text).values("title", "content", "url", "callback_data"))
        return {"ok": True, "bot": bot.robot_id, "matched_replies": replies, "received_text": text}
