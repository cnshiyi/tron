from django.db import models
from common.models import TimeStampedModel

class Bot(TimeStampedModel):
    robot_id = models.CharField(max_length=128, unique=True, verbose_name="机器人ID")
    token = models.CharField(max_length=256, verbose_name="Telegram Bot Token")
    username = models.CharField(max_length=128, blank=True, default="", verbose_name="机器人用户名")
    first_name = models.CharField(max_length=128, blank=True, default="", verbose_name="昵称")
    owner_user_id = models.CharField(max_length=128, blank=True, default="", verbose_name="归属用户ID")
    webhook_enabled = models.BooleanField(default=True, verbose_name="启用Webhook")
    broadcast_enabled = models.BooleanField(default=True, verbose_name="启用群组播报")

    def __str__(self):
        return self.username or self.robot_id

class Promotion(TimeStampedModel):
    POSITION_CHOICES = [("message", "消息"), ("button", "按钮")]
    TYPE_CHOICES = [("text", "文本"), ("inline", "内嵌按钮")]
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE, related_name="promotions", verbose_name="机器人")
    title = models.CharField(max_length=200, verbose_name="标题")
    command = models.CharField(max_length=100, blank=True, default="", verbose_name="命令")
    content = models.TextField(blank=True, default="", verbose_name="内容")
    url = models.URLField(blank=True, default="", verbose_name="链接")
    callback_data = models.CharField(max_length=255, blank=True, default="", verbose_name="回调内容")
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="text")
    position = models.CharField(max_length=20, choices=POSITION_CHOICES, default="message")
    auto_reply = models.BooleanField(default=False, verbose_name="自动回复")
    sort = models.IntegerField(default=0)
    row_place = models.IntegerField(default=0)

class BotGroup(TimeStampedModel):
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE, related_name="groups")
    chat_id = models.CharField(max_length=128, verbose_name="群组ID")
    title = models.CharField(max_length=255, blank=True, default="群组名称")
    broadcast_enabled = models.BooleanField(default=True, verbose_name="开启收益播报")
