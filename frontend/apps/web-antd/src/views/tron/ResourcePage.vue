<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import { Button, Card, Form, FormItem, Input, InputNumber, Modal, Popconfirm, Space, Switch, Table, Textarea, message } from 'ant-design-vue';
import { createResource, deleteResource, listResource, resourceConfigs, updateResource } from '#/api/tron';

const props = defineProps<{ key?: string }>();
const route = useRoute();
const keyName = computed(() => String(props.key || route.params.key || 'bots'));
const config = computed(() => resourceConfigs[keyName.value] || resourceConfigs.bots);
const loading = ref(false);
const rows = ref<Record<string, any>[]>([]);
const total = ref(0);
const page = ref(1);
const pageSize = ref(10);
const keyword = ref('');
const modalOpen = ref(false);
const saving = ref(false);
const form = reactive<Record<string, any>>({});

const columns = computed(() => [
  ...config.value.columns.map((col) => ({ ...col, ellipsis: col.ellipsis ?? true })),
  { title: '操作', key: 'action', fixed: 'right', width: 150 },
]);

function resetForm(record: Record<string, any> = {}) {
  Object.keys(form).forEach((k) => delete form[k]);
  config.value.fields.forEach((field) => {
    form[field.name] = record[field.name] ?? (field.type === 'boolean' ? false : '');
  });
  if (record.id) form.id = record.id;
}

async function load() {
  loading.value = true;
  try {
    const data = await listResource(config.value.endpoint, { page: page.value, page_size: pageSize.value, search: keyword.value });
    rows.value = data.results || [];
    total.value = data.count || rows.value.length;
  } catch (e: any) {
    message.error(e.message || String(e));
  } finally {
    loading.value = false;
  }
}

function add() { resetForm(); modalOpen.value = true; }
function edit(record: Record<string, any>) { resetForm(record); modalOpen.value = true; }

async function save() {
  saving.value = true;
  try {
    const payload = { ...form };
    Object.keys(payload).forEach((k) => payload[k] === '' && delete payload[k]);
    if (payload.id) await updateResource(config.value.endpoint, payload.id, payload);
    else await createResource(config.value.endpoint, payload);
    message.success('保存成功');
    modalOpen.value = false;
    await load();
  } catch (e: any) {
    message.error(e.message || String(e));
  } finally {
    saving.value = false;
  }
}

async function remove(record: Record<string, any>) {
  await deleteResource(config.value.endpoint, record.id);
  message.success('已删除');
  await load();
}

watch(keyName, () => { page.value = 1; load(); });
onMounted(load);
</script>

<template>
  <div class="p-5">
    <Card :title="config.title">
      <template #extra>
        <Space>
          <Input v-model:value="keyword" allow-clear placeholder="搜索" style="width: 220px" @press-enter="load" />
          <Button @click="load">刷新/查询</Button>
          <Button type="primary" @click="add">新增</Button>
        </Space>
      </template>
      <p v-if="config.description" class="mb-4 text-gray-500">{{ config.description }}</p>
      <Table
        row-key="id"
        :loading="loading"
        :columns="columns"
        :data-source="rows"
        :scroll="{ x: 1100 }"
        :pagination="{ current: page, pageSize, total, showSizeChanger: true }"
        @change="(p:any) => { page = p.current; pageSize = p.pageSize; load(); }"
      >
        <template #bodyCell="{ column, record, text }">
          <template v-if="column.key === 'action'">
            <Space>
              <Button size="small" type="link" @click="edit(record)">编辑</Button>
              <Popconfirm title="确定删除？" @confirm="remove(record)">
                <Button size="small" danger type="link">删除</Button>
              </Popconfirm>
            </Space>
          </template>
          <template v-else-if="typeof text === 'boolean'">
            {{ text ? '是' : '否' }}
          </template>
        </template>
      </Table>
    </Card>

    <Modal v-model:open="modalOpen" :title="form.id ? '编辑' : '新增'" :confirm-loading="saving" width="760px" @ok="save">
      <Form layout="vertical">
        <FormItem v-for="field in config.fields" :key="field.name" :label="field.label">
          <Switch v-if="field.type === 'boolean'" v-model:checked="form[field.name]" />
          <InputNumber v-else-if="field.type === 'number'" v-model:value="form[field.name]" class="w-full" />
          <Textarea v-else-if="field.type === 'textarea'" v-model:value="form[field.name]" :rows="4" />
          <Input v-else v-model:value="form[field.name]" />
        </FormItem>
      </Form>
    </Modal>
  </div>
</template>
