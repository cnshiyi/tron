<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { Button, Card, Select, Space, Table, Tag, message } from 'ant-design-vue';

const API_BASE = import.meta.env.VITE_TRON_API_URL || 'http://127.0.0.1:18001/api';

interface LegacyResource {
  resource: string;
  table_name: string;
  title: string;
}

const loading = ref(false);
const resources = ref<LegacyResource[]>([]);
const selectedResource = ref('tgConfig');
const rows = ref<Record<string, any>[]>([]);
const total = ref(0);
const page = ref(1);
const pageSize = ref(10);

const resourceOptions = computed(() => resources.value.map((item) => ({ label: `${item.title}（${item.resource}）`, value: item.resource })));
const selectedMeta = computed(() => resources.value.find((item) => item.resource === selectedResource.value));
const columns = computed(() => {
  const keys = Array.from(new Set(rows.value.flatMap((row) => Object.keys(row).filter((key) => !key.startsWith('_'))))).slice(0, 12);
  return keys.map((key) => ({ title: key, dataIndex: key, ellipsis: true, width: 160 }));
});

async function request<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`);
  if (!response.ok) throw new Error(await response.text());
  return response.json() as Promise<T>;
}

async function loadResources() {
  resources.value = await request<LegacyResource[]>('/legacy/game-records/resources/');
}

async function loadRows() {
  loading.value = true;
  try {
    const search = new URLSearchParams({ resource: selectedResource.value, page: String(page.value), page_size: String(pageSize.value) });
    const data = await request<{ count: number; results: Record<string, any>[] }>(`/legacy/game-records/?${search.toString()}`);
    rows.value = data.results || [];
    total.value = data.count || 0;
  } catch (error: any) {
    message.error(error.message || String(error));
  } finally {
    loading.value = false;
  }
}

async function refresh() {
  page.value = 1;
  await loadRows();
}

onMounted(async () => {
  await loadResources();
  await loadRows();
});
</script>

<template>
  <div class="p-5">
    <Card title="旧版TRX质押数据">
      <template #extra>
        <Space>
          <Select v-model:value="selectedResource" show-search style="width: 340px" :options="resourceOptions" @change="refresh" />
          <Button @click="loadRows">刷新</Button>
        </Space>
      </template>
      <p class="mb-4 text-gray-500">
        兼容旧版 Jeecg `TRX质押版本` 的 27 个 `/game/tg*` 页面和接口。旧 SQL 导入后，可在这里按资源查看原始字段。
      </p>
      <Space class="mb-4">
        <Tag color="blue">{{ selectedMeta?.title || selectedResource }}</Tag>
        <Tag>{{ selectedMeta?.table_name }}</Tag>
      </Space>
      <Table
        row-key="_record_id"
        :columns="columns"
        :data-source="rows"
        :loading="loading"
        :scroll="{ x: 1400 }"
        :pagination="{ current: page, pageSize, total, showSizeChanger: true }"
        @change="(p:any) => { page = p.current; pageSize = p.pageSize; loadRows(); }"
      />
    </Card>
  </div>
</template>
