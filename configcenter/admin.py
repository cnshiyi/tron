from django.contrib import admin

from .models import TextConfig


@admin.register(TextConfig)
class TextConfigAdmin(admin.ModelAdmin):
    list_display = ("key", "label", "category", "is_active", "sort", "updated_at")
    list_filter = ("category", "is_active")
    search_fields = ("key", "label", "value", "description")
