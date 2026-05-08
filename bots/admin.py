from django.contrib import admin
from .models import Bot, Promotion, BotGroup

@admin.register(Bot)
class BotAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Bot._meta.fields[:6]]
    search_fields = [f.name for f in Bot._meta.fields if f.__class__.__name__ in ('CharField', 'TextField')][:5]

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Promotion._meta.fields[:6]]
    search_fields = [f.name for f in Promotion._meta.fields if f.__class__.__name__ in ('CharField', 'TextField')][:5]

@admin.register(BotGroup)
class BotGroupAdmin(admin.ModelAdmin):
    list_display = [f.name for f in BotGroup._meta.fields[:6]]
    search_fields = [f.name for f in BotGroup._meta.fields if f.__class__.__name__ in ('CharField', 'TextField')][:5]
