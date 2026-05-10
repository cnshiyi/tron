import csv
import io
import uuid

from django.db import transaction
from django.http import HttpResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from .models import LegacyGameRecord
from .resources import RESOURCE_TABLE_MAP, RESOURCE_TITLES
from .serializers import LegacyGameRecordSerializer


def _legacy_success(result=None, message="操作成功", **extra):
    payload = {"success": True, "message": message, "code": 200}
    if result is not None:
        payload["result"] = result
    payload.update(extra)
    return Response(payload)


def _resource_or_error(resource):
    table_name = RESOURCE_TABLE_MAP.get(resource)
    if not table_name:
        return None, Response(
            {"success": False, "message": f"未知旧版资源: {resource}", "code": 404},
            status=status.HTTP_404_NOT_FOUND,
        )
    return table_name, None


def _normalize_payload(data):
    if hasattr(data, "dict"):
        data = data.dict()
    return dict(data or {})


def _queryset_for(resource):
    return LegacyGameRecord.objects.filter(resource=resource, is_active=True).order_by("-updated_at", "-id")


@api_view(["GET", "POST", "PUT", "DELETE"])
def legacy_game_endpoint(request, resource, legacy_action):
    table_name, error = _resource_or_error(resource)
    if error:
        return error

    if legacy_action == "list":
        queryset = _queryset_for(resource)
        query = request.query_params
        for key, value in query.items():
            if key in {"pageNo", "page", "pageSize", "page_size", "column", "order"} or value == "":
                continue
            queryset = queryset.filter(data__contains={key: value})
        page_no = int(query.get("pageNo") or query.get("page") or 1)
        page_size = int(query.get("pageSize") or query.get("page_size") or 10)
        total = queryset.count()
        start = max(page_no - 1, 0) * page_size
        records = LegacyGameRecordSerializer(queryset[start:start + page_size], many=True).data
        return _legacy_success({
            "records": records,
            "total": total,
            "size": page_size,
            "current": page_no,
            "pages": (total + page_size - 1) // page_size,
        })

    if legacy_action == "queryById":
        legacy_id = request.query_params.get("id") or request.data.get("id")
        record = _queryset_for(resource).filter(legacy_id=legacy_id).first()
        if not record:
            return Response({"success": False, "message": "记录不存在", "code": 404}, status=status.HTTP_404_NOT_FOUND)
        return _legacy_success(LegacyGameRecordSerializer(record).data)

    if legacy_action in {"add", "edit"}:
        payload = _normalize_payload(request.data)
        legacy_id = str(payload.get("id") or uuid.uuid4().hex)
        payload["id"] = legacy_id
        record, _ = LegacyGameRecord.objects.update_or_create(
            resource=resource,
            legacy_id=legacy_id,
            defaults={"table_name": table_name, "data": payload, "is_active": True},
        )
        return _legacy_success(LegacyGameRecordSerializer(record).data)

    if legacy_action == "delete":
        legacy_id = request.query_params.get("id") or request.data.get("id")
        count = LegacyGameRecord.objects.filter(resource=resource, legacy_id=legacy_id).update(is_active=False)
        return _legacy_success({"deleted": count})

    if legacy_action == "deleteBatch":
        ids = request.query_params.get("ids") or request.data.get("ids") or ""
        id_list = [item.strip() for item in ids.split(",") if item.strip()] if isinstance(ids, str) else [str(item) for item in ids]
        count = LegacyGameRecord.objects.filter(resource=resource, legacy_id__in=id_list).update(is_active=False)
        return _legacy_success({"deleted": count})

    if legacy_action == "exportXls":
        records = list(_queryset_for(resource))
        fieldnames = sorted({key for record in records for key in (record.data or {}).keys()}) or ["id"]
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow({key: (record.data or {}).get(key, "") for key in fieldnames})
        response = HttpResponse(buffer.getvalue(), content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = f'attachment; filename="{resource}.csv"'
        return response

    return Response({"success": False, "message": f"暂不支持操作: {legacy_action}", "code": 400}, status=status.HTTP_400_BAD_REQUEST)


class LegacyGameRecordViewSet(viewsets.ModelViewSet):
    serializer_class = LegacyGameRecordSerializer
    filterset_fields = ["resource", "table_name", "is_active"]
    search_fields = ["resource", "table_name", "legacy_id"]

    def get_queryset(self):
        return LegacyGameRecord.objects.all().order_by("resource", "-updated_at")

    @action(detail=False, methods=["get"], url_path="resources")
    def resources(self, request):
        return Response([
            {"resource": resource, "table_name": table, "title": RESOURCE_TITLES.get(resource, resource)}
            for resource, table in RESOURCE_TABLE_MAP.items()
        ])

    @action(detail=False, methods=["post"], url_path="restore")
    def restore(self, request):
        ids = request.data.get("ids") or []
        with transaction.atomic():
            count = LegacyGameRecord.objects.filter(id__in=ids).update(is_active=True)
        return Response({"restored": count})
