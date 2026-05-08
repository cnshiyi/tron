from django.db import models

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_active = models.BooleanField(default=True, verbose_name="启用")
    remark = models.TextField(blank=True, default="", verbose_name="备注")

    class Meta:
        abstract = True
        ordering = ["-created_at"]
