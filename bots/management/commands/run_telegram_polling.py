import json
import time

import httpx
from django.conf import settings
from django.core.management.base import BaseCommand

from bots.models import Bot
from bots.services import TelegramBotService


class Command(BaseCommand):
    help = "使用 Telegram getUpdates 轮询机器人消息，不需要公网域名。"

    def add_arguments(self, parser):
        parser.add_argument("--bot-id", default="", help="只轮询指定 robot_id；默认轮询所有启用 Webhook 的机器人")
        parser.add_argument("--once", action="store_true", help="只拉取一次，用于联调验证")
        parser.add_argument("--timeout", type=int, default=30, help="Telegram long polling timeout")
        parser.add_argument("--sleep", type=float, default=1.0, help="每轮之间的休眠秒数")
        parser.add_argument("--limit", type=int, default=100, help="每轮最多拉取更新数")
        parser.add_argument("--dry-run", action="store_true", help="强制不真实回复消息，仅处理入库和匹配逻辑")

    def handle(self, *args, **options):
        qs = Bot.objects.filter(is_active=True, webhook_enabled=True, token__gt="")
        if options["bot_id"]:
            qs = qs.filter(robot_id=options["bot_id"])
        bots = list(qs.order_by("id"))
        if not bots:
            self.stdout.write(self.style.WARNING("没有可轮询的机器人"))
            return

        service = TelegramBotService()
        offsets = {bot.robot_id: None for bot in bots}
        dry_run = options["dry_run"] or not settings.TELEGRAM_SEND_ENABLED
        self.stdout.write(self.style.SUCCESS(
            f"启动 Telegram 轮询模式：bots={len(bots)} dry_run={dry_run} send_enabled={settings.TELEGRAM_SEND_ENABLED}"
        ))

        while True:
            for bot in bots:
                params = {
                    "timeout": options["timeout"],
                    "limit": options["limit"],
                    "allowed_updates": json.dumps(["message", "callback_query"]),
                }
                if offsets[bot.robot_id] is not None:
                    params["offset"] = offsets[bot.robot_id]
                try:
                    response = httpx.get(service.telegram_api_url(bot, "getUpdates"), params=params, timeout=options["timeout"] + 10)
                    data = response.json()
                    if not response.is_success or not data.get("ok"):
                        self.stdout.write(self.style.WARNING(f"{bot.robot_id} getUpdates 失败：{data}"))
                        continue
                    for update in data.get("result", []):
                        offsets[bot.robot_id] = int(update.get("update_id", 0)) + 1
                        result = service.handle_update(bot, update, force_dry_run=dry_run)
                        self.stdout.write(f"{bot.robot_id} update={update.get('update_id')} result={result}")
                except Exception as exc:  # pragma: no cover - network/runtime protection
                    self.stdout.write(self.style.WARNING(f"{bot.robot_id} 轮询异常：{exc}"))
            if options["once"]:
                return
            time.sleep(options["sleep"])
