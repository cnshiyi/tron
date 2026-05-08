from django.contrib import admin
from .models import MemberGoods, MemberOrder

@admin.register(MemberGoods)
class MemberGoodsAdmin(admin.ModelAdmin):
    list_display = [f.name for f in MemberGoods._meta.fields[:6]]
    search_fields = [f.name for f in MemberGoods._meta.fields if f.__class__.__name__ in ('CharField', 'TextField')][:5]

@admin.register(MemberOrder)
class MemberOrderAdmin(admin.ModelAdmin):
    list_display = [f.name for f in MemberOrder._meta.fields[:6]]
    search_fields = [f.name for f in MemberOrder._meta.fields if f.__class__.__name__ in ('CharField', 'TextField')][:5]
