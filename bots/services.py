import json
from dataclasses import dataclass
from typing import Any

import httpx
from django.conf import settings

from tgusers.models import TgUser
from .models import Bot, BotGroup, BroadcastLog, Promotion


@dataclass
class TelegramSendResult:
    ok: bool
    message_id: str = ""
    error: str = ""
    payload: dict[str, Any] | None = None


class TelegramBotService:
    def telegram_api_url(self, bot: Bot, method: str) -> str:
        return f"https://api.telegram.org/bot{bot.token}/{method}"

    def send_message(self, bot: Bot, chat_id: str, text: str, reply_markup: dict | None = None, dry_run: bool | None = None) -> TelegramSendResult:
        payload: dict[str, Any] = {"chat_id": chat_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": False}
        if reply_markup:
            payload["reply_markup"] = reply_markup
        if dry_run is None:
            dry_run = not getattr(settings, "TELEGRAM_SEND_ENABLED", False)
        if dry_run:
            return TelegramSendResult(ok=True, message_id="dry-run", payload=payload)
        try:
            with httpx.Client(timeout=15) as client:
                response = client.post(self.telegram_api_url(bot, "sendMessage"), json=payload)
                data = response.json()
            if response.is_success and data.get("ok"):
                return TelegramSendResult(ok=True, message_id=str(data.get("result", {}).get("message_id", "")), payload=data)
            return TelegramSendResult(ok=False, error=json.dumps(data, ensure_ascii=False), payload=data)
        except Exception as exc:  # pragma: no cover - network protection
            return TelegramSendResult(ok=False, error=str(exc), payload=payload)

    def set_webhook(self, bot: Bot, base_url: str = "", drop_pending_updates: bool = True, dry_run: bool = True) -> dict:
        webhook_base = base_url.rstrip("/") or getattr(settings, "PUBLIC_BASE_URL", "").rstrip("/")
        webhook_url = f"{webhook_base}/api/telegram/webhook/{bot.robot_id}/" if webhook_base else ""
        payload = {"url": webhook_url, "drop_pending_updates": drop_pending_updates}
        if dry_run or not getattr(settings, "TELEGRAM_SEND_ENABLED", False):
            return {"ok": True, "dry_run": True, "webhook_url": webhook_url, "payload": payload}
        with httpx.Client(timeout=15) as client:
            response = client.post(self.telegram_api_url(bot, "setWebhook"), json=payload)
            return response.json()

    def build_reply_markup(self, bot: Bot) -> dict | None:
        buttons = []
        promotions = Promotion.objects.filter(bot=bot, is_active=True, position="button").order_by("row_place", "sort", "id")
        current_row = None
        row: list[dict[str, str]] = []
        for item in promotions:
            if current_row is None:
                current_row = item.row_place
            if item.row_place != current_row and row:
                buttons.append(row)
                row = []
                current_row = item.row_place
            button = {"text": item.title}
            if item.url:
                button["url"] = item.url
            else:
                button["callback_data"] = item.callback_data or item.command or item.title
            row.append(button)
        if row:
            buttons.append(row)
        return {"inline_keyboard": buttons} if buttons else None

    def upsert_user_and_group(self, bot: Bot, update: dict) -> tuple[TgUser | None, BotGroup | None, str, str]:
        callback = update.get("callback_query") or {}
        message = update.get("message") or callback.get("message") or {}
        chat = message.get("chat") or {}
        from_user = message.get("from") or callback.get("from") or {}
        text = message.get("text") or callback.get("data") or ""
        chat_id = str(chat.get("id") or "")
        user_id = str(from_user.get("id") or "")
        user_obj = None
        if user_id:
            inviter_id = ""
            if text.startswith("/start "):
                inviter_id = text.split(maxsplit=1)[1].strip()[:128]
            defaults = {
                "bot_id": bot.robot_id,
                "username": from_user.get("username", "") or "",
                "first_name": from_user.get("first_name", "") or "",
            }
            if inviter_id and inviter_id != user_id:
                defaults["inviter_id"] = inviter_id
            user_obj, created = TgUser.objects.update_or_create(user_id=user_id, defaults=defaults)
            if not created and inviter_id and not user_obj.inviter_id and inviter_id != user_id:
                user_obj.inviter_id = inviter_id
                user_obj.save(update_fields=["inviter_id", "updated_at"])
        group_obj = None
        if chat_id and chat.get("type") in {"group", "supergroup", "channel"}:
            group_obj, _ = BotGroup.objects.update_or_create(
                bot=bot, chat_id=chat_id, defaults={"title": chat.get("title", "") or "群组名称"}
            )
        return user_obj, group_obj, chat_id, text

    def handle_update(self, bot: Bot, update: dict, force_dry_run: bool | None = None) -> dict:
        user_obj, group_obj, chat_id, text = self.upsert_user_and_group(bot, update)
        if user_obj and user_obj.is_blacklisted:
            return {"ok": True, "ignored": "blacklisted", "user_id": user_obj.user_id}

        commands = [text]
        if text.startswith("/") and " " in text:
            commands.append(text.split(maxsplit=1)[0])
        if text.startswith("/start"):
            commands.append("/start")

        replies = list(Promotion.objects.filter(bot=bot, is_active=True, auto_reply=True, position="message", command__in=commands).order_by("sort", "id"))
        sent = []
        reply_markup = self.build_reply_markup(bot)
        if chat_id:
            for item in replies:
                result = self.send_message(bot, chat_id, item.content or item.title, reply_markup=reply_markup, dry_run=force_dry_run)
                sent.append({"promotion": item.id, "ok": result.ok, "message_id": result.message_id, "error": result.error})
        return {
            "ok": True,
            "bot": bot.robot_id,
            "chat_id": chat_id,
            "user_id": getattr(user_obj, "user_id", ""),
            "group_id": getattr(group_obj, "id", None),
            "matched_replies": [{"id": r.id, "title": r.title, "content": r.content} for r in replies],
            "sent": sent,
            "received_text": text,
        }

    def handle_webhook(self, bot_id: str, raw_body: bytes) -> dict:
        try:
            update = json.loads(raw_body.decode("utf-8"))
        except Exception as exc:
            return {"ok": False, "error": f"invalid json: {exc}"}
        bot = Bot.objects.filter(robot_id=bot_id, is_active=True, webhook_enabled=True).first()
        if not bot:
            return {"ok": False, "error": "bot not found or webhook disabled"}
        return self.handle_update(bot, update)

    def broadcast(self, bot: Bot, content: str, title: str = "", chat_id: str = "", dry_run: bool = True) -> dict:
        targets = []
        if chat_id:
            targets.append((None, chat_id))
        else:
            groups = BotGroup.objects.filter(bot=bot, is_active=True, broadcast_enabled=True).order_by("id")
            targets.extend((group, group.chat_id) for group in groups)
        logs = []
        for group, target_chat_id in targets:
            result = self.send_message(bot, target_chat_id, content, dry_run=dry_run)
            log = BroadcastLog.objects.create(
                bot=bot,
                group=group,
                chat_id=target_chat_id,
                title=title,
                content=content,
                status="dry_run" if dry_run else "sent" if result.ok else "failed",
                telegram_message_id=result.message_id,
                error_message=result.error,
                payload=result.payload or {},
            )
            logs.append({"id": log.id, "chat_id": target_chat_id, "status": log.status, "message_id": log.telegram_message_id, "error": log.error_message})
        return {"ok": True, "target_count": len(targets), "logs": logs, "dry_run": dry_run}
