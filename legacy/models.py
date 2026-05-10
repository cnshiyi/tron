from django.db import models

from common.models import TimeStampedModel


class LegacyGameRecord(TimeStampedModel):
    """旧版 TRX 质押 Jeecg `/game/tg*` 表记录的兼容存储。"""

    resource = models.CharField(max_length=100, db_index=True, verbose_name="旧版资源名")
    table_name = models.CharField(max_length=100, db_index=True, verbose_name="旧版表名")
    legacy_id = models.CharField(max_length=255, db_index=True, verbose_name="旧版ID")
    data = models.JSONField(default=dict, blank=True, verbose_name="旧版字段数据")

    class Meta:
        unique_together = [("resource", "legacy_id")]
        indexes = [
            models.Index(fields=["resource", "is_active"]),
            models.Index(fields=["table_name", "legacy_id"]),
        ]
        verbose_name = "旧版TRX质押记录"
        verbose_name_plural = "旧版TRX质押记录"

    def __str__(self):
        return f"{self.resource}:{self.legacy_id}"
