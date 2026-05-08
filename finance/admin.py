from django.contrib import admin
from .models import Balance, RunningWater, Withdrawal

@admin.register(Balance)
class BalanceAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Balance._meta.fields[:6]]
    search_fields = [f.name for f in Balance._meta.fields if f.__class__.__name__ in ('CharField', 'TextField')][:5]

@admin.register(RunningWater)
class RunningWaterAdmin(admin.ModelAdmin):
    list_display = [f.name for f in RunningWater._meta.fields[:6]]
    search_fields = [f.name for f in RunningWater._meta.fields if f.__class__.__name__ in ('CharField', 'TextField')][:5]

@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Withdrawal._meta.fields[:6]]
    search_fields = [f.name for f in Withdrawal._meta.fields if f.__class__.__name__ in ('CharField', 'TextField')][:5]
