from django.conf import settings
from django.core.management.base import BaseCommand

from bots.models import Bot
from energy.models import StakingAccount


class Command(BaseCommand):
    help = "检查 TRON 项目线上实测前的配置就绪度，不发送消息、不广播链上交易。"

    def add_arguments(self, parser):
        parser.add_argument("--strict", action="store_true", help="缺少线上必需项时返回非零退出码")

    def handle(self, *args, **options):
        checks = []

        def add(name, ok, message):
            checks.append((name, ok, message))
            style = self.style.SUCCESS if ok else self.style.WARNING
            self.stdout.write(style(f"{'✅' if ok else '⚠️'} {name}: {message}"))

        add("DEBUG", not settings.DEBUG, "已关闭" if not settings.DEBUG else "仍为开发模式，线上实测建议关闭")
        add("ALLOWED_HOSTS", bool(settings.ALLOWED_HOSTS), ",".join(settings.ALLOWED_HOSTS) or "未配置")
        delivery_mode = getattr(settings, "TELEGRAM_DELIVERY_MODE", "polling")
        uses_polling = delivery_mode == "polling"
        add("TELEGRAM_DELIVERY_MODE", delivery_mode in {"polling", "webhook"}, f"{delivery_mode}（polling 不需要域名，webhook 需要公网 HTTPS）")
        add("PUBLIC_BASE_URL", uses_polling or bool(settings.PUBLIC_BASE_URL), "轮询模式不需要公网地址" if uses_polling else settings.PUBLIC_BASE_URL or "未配置公网地址，无法设置 Telegram Webhook")
        add("TRONGRID_API_KEY", bool(settings.TRONGRID_API_KEY), "已配置" if settings.TRONGRID_API_KEY else "未配置，主网限流风险较高")
        add("TELEGRAM_SEND_ENABLED", settings.TELEGRAM_SEND_ENABLED, "已开启真实发送" if settings.TELEGRAM_SEND_ENABLED else "关闭，当前只会 dry-run")
        add("SOHU_SEND_ENABLED", settings.SOHU_SEND_ENABLED, "已开启三方能量真实请求" if settings.SOHU_SEND_ENABLED else "关闭，当前只会 dry-run")
        add("WITHDRAWAL_PAYOUT_ENABLED", settings.WITHDRAWAL_PAYOUT_ENABLED, "已开启真实出款" if settings.WITHDRAWAL_PAYOUT_ENABLED else "关闭，当前不会真实出款")
        add("Bot token", Bot.objects.filter(is_active=True, token__gt="").exists(), f"已配置 {Bot.objects.filter(is_active=True, token__gt='').count()} 个机器人")
        add("StakingAccount", StakingAccount.objects.filter(enabled=True).exists(), f"已配置 {StakingAccount.objects.filter(enabled=True).count()} 个启用质押账户")

        required = ["TELEGRAM_DELIVERY_MODE", "TRONGRID_API_KEY", "Bot token", "StakingAccount"]
        if not uses_polling:
            required.append("PUBLIC_BASE_URL")
        missing = [name for name, ok, _ in checks if name in required and not ok]
        if missing:
            self.stdout.write(self.style.WARNING(f"线上实测仍缺：{', '.join(missing)}"))
            if options["strict"]:
                raise SystemExit(1)
            return
        self.stdout.write(self.style.SUCCESS("线上实测基础配置已就绪。"))
