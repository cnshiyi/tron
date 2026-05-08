from django.contrib import admin
from .models import ExchangeConfig, ExchangeOrder, ExchangeBlacklist

@admin.register(ExchangeConfig)
class ExchangeConfigAdmin(admin.ModelAdmin):
    list_display = [f.name for f in ExchangeConfig._meta.fields[:6]]
    search_fields = [f.name for f in ExchangeConfig._meta.fields if f.__class__.__name__ in ('CharField', 'TextField')][:5]

@admin.register(ExchangeOrder)
class ExchangeOrderAdmin(admin.ModelAdmin):
    list_display = [f.name for f in ExchangeOrder._meta.fields[:6]]
    search_fields = [f.name for f in ExchangeOrder._meta.fields if f.__class__.__name__ in ('CharField', 'TextField')][:5]

@admin.register(ExchangeBlacklist)
class ExchangeBlacklistAdmin(admin.ModelAdmin):
    list_display = [f.name for f in ExchangeBlacklist._meta.fields[:6]]
    search_fields = [f.name for f in ExchangeBlacklist._meta.fields if f.__class__.__name__ in ('CharField', 'TextField')][:5]
