from django.contrib import admin
from .models import EnergyPlan, EnergyOrder, EnergyCommission

@admin.register(EnergyPlan)
class EnergyPlanAdmin(admin.ModelAdmin):
    list_display = [f.name for f in EnergyPlan._meta.fields[:6]]
    search_fields = [f.name for f in EnergyPlan._meta.fields if f.__class__.__name__ in ('CharField', 'TextField')][:5]

@admin.register(EnergyOrder)
class EnergyOrderAdmin(admin.ModelAdmin):
    list_display = [f.name for f in EnergyOrder._meta.fields[:6]]
    search_fields = [f.name for f in EnergyOrder._meta.fields if f.__class__.__name__ in ('CharField', 'TextField')][:5]

@admin.register(EnergyCommission)
class EnergyCommissionAdmin(admin.ModelAdmin):
    list_display = [f.name for f in EnergyCommission._meta.fields[:6]]
    search_fields = [f.name for f in EnergyCommission._meta.fields if f.__class__.__name__ in ('CharField', 'TextField')][:5]
