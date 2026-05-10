import ast
import re
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from legacy.models import LegacyGameRecord
from legacy.resources import TABLE_RESOURCE_MAP

CREATE_TABLE_RE = re.compile(r"CREATE TABLE `([^`]+)`\s*\((.*?)\) ENGINE", re.S)
INSERT_RE = re.compile(r"INSERT INTO `([^`]+)` VALUES (.*?);", re.S)


def split_sql_values(values_sql):
    rows = []
    depth = 0
    start = None
    in_string = False
    escape = False
    for index, char in enumerate(values_sql):
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == "'":
                in_string = False
            continue
        if char == "'":
            in_string = True
        elif char == "(":
            if depth == 0:
                start = index
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0 and start is not None:
                rows.append(values_sql[start:index + 1])
                start = None
    return rows


def mysql_tuple_to_python(row_sql):
    value = row_sql.replace("\\'", "'")
    value = re.sub(r"\bNULL\b", "None", value, flags=re.I)
    return ast.literal_eval(value)


def table_columns(sql_text):
    columns = {}
    for table_name, body in CREATE_TABLE_RE.findall(sql_text):
        fields = []
        for line in body.splitlines():
            line = line.strip()
            if not line.startswith("`"):
                continue
            fields.append(line.split("`", 2)[1])
        columns[table_name] = fields
    return columns


class Command(BaseCommand):
    help = "导入 TRX质押版本 Jeecg SQL 中的 tg_* 业务表到旧版兼容存储。"

    def add_arguments(self, parser):
        parser.add_argument("sql_path", type=str)
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--clear", action="store_true", help="导入前清空旧版兼容记录")

    def handle(self, *args, **options):
        sql_path = Path(options["sql_path"]).expanduser()
        if not sql_path.exists():
            raise CommandError(f"SQL 文件不存在: {sql_path}")

        sql_text = sql_path.read_text(errors="ignore")
        columns = table_columns(sql_text)
        totals = {resource: 0 for resource in TABLE_RESOURCE_MAP.values()}
        rows_to_save = []

        for table_name, values_sql in INSERT_RE.findall(sql_text):
            resource = TABLE_RESOURCE_MAP.get(table_name)
            if not resource:
                continue
            field_names = columns.get(table_name) or []
            for row_sql in split_sql_values(values_sql):
                values = mysql_tuple_to_python(row_sql)
                if not isinstance(values, tuple):
                    values = (values,)
                data = {field: value for field, value in zip(field_names, values)}
                legacy_id = str(data.get("id") or data.get("hash") or f"{resource}-{totals[resource] + 1}")
                rows_to_save.append((resource, table_name, legacy_id, data))
                totals[resource] += 1

        if options["dry_run"]:
            self.stdout.write(self.style.WARNING(f"dry-run: parsed {len(rows_to_save)} legacy tg rows"))
            for resource, count in sorted(totals.items()):
                if count:
                    self.stdout.write(f"{resource}: {count}")
            return

        with transaction.atomic():
            if options["clear"]:
                LegacyGameRecord.objects.all().delete()
            for resource, table_name, legacy_id, data in rows_to_save:
                LegacyGameRecord.objects.update_or_create(
                    resource=resource,
                    legacy_id=legacy_id,
                    defaults={"table_name": table_name, "data": data, "is_active": True},
                )

        self.stdout.write(self.style.SUCCESS(f"imported {len(rows_to_save)} legacy tg rows"))
        for resource, count in sorted(totals.items()):
            if count:
                self.stdout.write(f"{resource}: {count}")
