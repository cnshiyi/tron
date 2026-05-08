from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from .models import TextConfig
from .serializers import TextConfigSerializer


class TextConfigViewSet(viewsets.ModelViewSet):
    queryset = TextConfig.objects.all()
    serializer_class = TextConfigSerializer
    filterset_fields = ["category", "is_active"]
    search_fields = ["key", "label", "value", "description"]
    ordering_fields = ["category", "sort", "key", "updated_at"]

    @action(detail=False, methods=["post"], url_path="sync-defaults")
    def sync_defaults(self, request):
        """从前端提交的默认文案中补齐后台配置项，不覆盖管理员已修改的 value。"""
        items = request.data.get("items") or []
        if not isinstance(items, list):
            return Response({"detail": "items must be a list"}, status=status.HTTP_400_BAD_REQUEST)

        created = 0
        updated = 0
        with transaction.atomic():
            for index, item in enumerate(items):
                key = str(item.get("key") or "").strip()
                if not key:
                    continue
                defaults = {
                    "label": item.get("label") or key,
                    "value": item.get("value") or "",
                    "default_value": item.get("value") or "",
                    "category": item.get("category") or "ui",
                    "description": item.get("description") or "",
                    "sort": item.get("sort", index),
                }
                obj, was_created = TextConfig.objects.get_or_create(key=key, defaults=defaults)
                if was_created:
                    created += 1
                    continue
                changed = False
                for field in ["label", "default_value", "category", "description", "sort"]:
                    new_value = defaults[field]
                    if getattr(obj, field) != new_value:
                        setattr(obj, field, new_value)
                        changed = True
                if changed:
                    obj.save(update_fields=["label", "default_value", "category", "description", "sort", "updated_at"])
                    updated += 1
        return Response({"created": created, "updated": updated, "total": len(items)})


@api_view(["GET"])
def ui_text(request):
    """前端启动时读取所有启用文案配置。"""
    category = request.query_params.get("category")
    qs = TextConfig.objects.filter(is_active=True)
    if category:
        qs = qs.filter(category=category)
    data = {row.key: row.value for row in qs.only("key", "value")}
    return Response(data)
