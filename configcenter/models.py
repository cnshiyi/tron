from django.db import models

from common.models import TimeStampedModel


class TextConfig(TimeStampedModel):
    """后台可配置的前端/机器人文案。"""

    key = models.CharField(max_length=200, unique=True, db_index=True, verbose_name="配置键")
    label = models.CharField(max_length=200, blank=True, default="", verbose_name="显示名称")
    value = models.TextField(blank=True, default="", verbose_name="配置值")
    default_value = models.TextField(blank=True, default="", verbose_name="默认值")
    category = models.CharField(max_length=80, blank=True, default="ui", db_index=True, verbose_name="分类")
    description = models.TextField(blank=True, default="", verbose_name="说明")
    sort = models.IntegerField(default=0, verbose_name="排序")

    class Meta:
        ordering = ["category", "sort", "key"]
        verbose_name = "文字配置"
        verbose_name_plural = "文字配置"

    def __str__(self):
        return f"{self.key}: {self.value[:30]}"
