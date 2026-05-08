from django.contrib import admin
from .models import Address, ChainTransaction

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Address._meta.fields[:6]]
    search_fields = [f.name for f in Address._meta.fields if f.__class__.__name__ in ('CharField', 'TextField')][:5]

@admin.register(ChainTransaction)
class ChainTransactionAdmin(admin.ModelAdmin):
    list_display = [f.name for f in ChainTransaction._meta.fields[:6]]
    search_fields = [f.name for f in ChainTransaction._meta.fields if f.__class__.__name__ in ('CharField', 'TextField')][:5]
