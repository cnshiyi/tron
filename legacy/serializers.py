from rest_framework import serializers

from .models import LegacyGameRecord


class LegacyGameRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegacyGameRecord
        fields = "__all__"

    def to_representation(self, instance):
        payload = dict(instance.data or {})
        payload.setdefault("id", instance.legacy_id)
        payload.setdefault("_record_id", instance.id)
        payload.setdefault("_resource", instance.resource)
        payload.setdefault("_table_name", instance.table_name)
        payload.setdefault("_is_active", instance.is_active)
        payload.setdefault("_created_at", instance.created_at)
        payload.setdefault("_updated_at", instance.updated_at)
        return payload
