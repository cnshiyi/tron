from django.contrib import admin

from .models import LegacyGameRecord


@admin.register(LegacyGameRecord)
class LegacyGameRecordAdmin(admin.ModelAdmin):
    list_display = ["resource", "table_name", "legacy_id", "is_active", "updated_at"]
    list_filter = ["resource", "table_name", "is_active"]
    search_fields = ["resource", "table_name", "legacy_id"]
