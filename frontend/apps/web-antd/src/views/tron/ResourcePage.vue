<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import { Button, Card, Form, FormItem, Input, InputNumber, Modal, Popconfirm, Space, Switch, Table, Textarea, message } from 'ant-design-vue';
import { actionResource, bulkCreateBots, createResource, deleteResource, getResourceConfig, listResource, loadUiText, uiText, updateResource } from '#/api/tron';

const props = defineProps<{ resourceKey?: string }>();
const route = useRoute();
const keyName = computed(() => String(props.resourceKey || route.params.key || 'bots'));
const textVersion = ref(0);
const config = computed(() => {
  textVersion.value;
  return getResourceConfig(keyName.value);
});
const t = uiText;
const loading = ref(false);
const rows = ref<Record<string, any>[]>([]);
const total = ref(0);
const page = ref(1);
const pageSize = ref(10);
const keyword = ref('');
const modalOpen = ref(false);
const saving = ref(false);
const form = reactive<Record<string, any>>({});
const bulkOpen = ref(false);
const bulkSaving = ref(false);
const bulkForm = reactive({ content: '', default_owner_user_id: '', webhook_enabled: true, broadcast_enabled: true });

const columns = computed(() => [
  ...config.value.columns.map((col) => ({ ...col, ellipsis: col.ellipsis ?? true })),
  { title: t('common.action', '操作'), key: 'action', fixed: 'right', width: config.value.actions?.length ? 360 : 150 },
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
    message.success(t('common.save_success', '保存成功'));
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
  message.success(t('common.delete_success', '已删除'));
  await load();
}

async function runCustomAction(action: Record<string, any>, record: Record<string, any>) {
  if (action.confirm && !window.confirm(action.confirm)) return;
  const payload = { ...(action.payload || {}) };
  if (action.promptField) {
    const value = window.prompt(action.promptLabel || t('common.input_prompt', '请输入'));
    if (!value) return;
    payload[action.promptField] = value;
  }
  try {
    await actionResource(config.value.endpoint, record.id, action.path, payload);
    message.success(t('common.action_success', '操作成功'));
    await load();
  } catch (e: any) {
    message.error(e.message || String(e));
  }
}
async function saveBulkBots() {
  bulkSaving.value = true;
  try {
    const result = await bulkCreateBots({ ...bulkForm });
    message.success(t('resource.bulk_success_template', '批量添加完成：新增 {created} 个，跳过 {skipped} 个，错误 {errors} 个')
      .replace('{created}', String(result.created_count))
      .replace('{skipped}', String(result.skipped?.length || 0))
      .replace('{errors}', String(result.errors?.length || 0)));
    bulkOpen.value = false;
    bulkForm.content = '';
    await load();
  } catch (e: any) {
    message.error(e.message || String(e));
  } finally {
    bulkSaving.value = false;
  }
}


watch(keyName, () => { page.value = 1; load(); });
onMounted(async () => {
  await loadUiText().catch(() => undefined);
  textVersion.value += 1;
  await load();
});
</script>

<template>
  <div class="p-5">
    <Card :title="config.title">
      <template #extra>
        <Space>
          <Input v-model:value="keyword" allow-clear :placeholder="t('common.search_placeholder', '搜索')" style="width: 220px" @press-enter="load" />
          <Button @click="load">{{ t('common.refresh_query', '刷新/查询') }}</Button>
          <Button v-if="keyName === 'bots'" @click="bulkOpen = true">{{ t('resource.bulk_add_bots', '批量添加机器人') }}</Button>
          <Button type="primary" @click="add">{{ t('common.add', '新增') }}</Button>
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
              <Button size="small" type="link" @click="edit(record)">{{ t('common.edit', '编辑') }}</Button>
              <Button
                v-for="item in config.actions || []"
                :key="item.name"
                size="small"
                :danger="item.danger"
                type="link"
                @click="runCustomAction(item, record)"
              >{{ item.label }}</Button>
              <Popconfirm :title="t('common.confirm_delete', '确定删除？')" @confirm="remove(record)">
                <Button size="small" danger type="link">{{ t('common.delete', '删除') }}</Button>
              </Popconfirm>
            </Space>
          </template>
          <template v-else-if="typeof text === 'boolean'">
            {{ text ? t('common.yes', '是') : t('common.no', '否') }}
          </template>
        </template>
      </Table>
    </Card>

    <Modal v-model:open="modalOpen" :title="form.id ? t('common.edit', '编辑') : t('common.add', '新增')" :confirm-loading="saving" width="760px" @ok="save">
      <Form layout="vertical">
        <FormItem v-for="field in config.fields" :key="field.name" :label="field.label">
          <Switch v-if="field.type === 'boolean'" v-model:checked="form[field.name]" />
          <InputNumber v-else-if="field.type === 'number'" v-model:value="form[field.name]" class="w-full" />
          <Textarea v-else-if="field.type === 'textarea'" v-model:value="form[field.name]" :rows="4" />
          <Input v-else v-model:value="form[field.name]" />
        </FormItem>
      </Form>
    </Modal>

    <Modal v-model:open="bulkOpen" :title="t('resource.bulk_add_bots', '批量添加机器人')" :confirm-loading="bulkSaving" width="820px" @ok="saveBulkBots">
      <Form layout="vertical">
        <FormItem :label="t('resource.bulk_owner', '默认归属用户ID')">
          <Input v-model:value="bulkForm.default_owner_user_id" :placeholder="t('resource.bulk_owner_placeholder', '可选，未填写则为空')" />
        </FormItem>
        <FormItem :label="t('resource.bulk_webhook', '启用Webhook')">
          <Switch v-model:checked="bulkForm.webhook_enabled" />
        </FormItem>
        <FormItem :label="t('resource.bulk_broadcast', '启用群组播报')">
          <Switch v-model:checked="bulkForm.broadcast_enabled" />
        </FormItem>
        <FormItem :label="t('resource.bulk_list', '机器人列表')">
          <Textarea
            v-model:value="bulkForm.content"
            :rows="10"
            :placeholder="t('resource.bulk_placeholder', '每行一个机器人，支持：token 或 robot_id,token 或 robot_id|token|username|昵称|归属用户ID')"
          />
        </FormItem>
        <p class="text-gray-500">{{ t('resource.bulk_example', '示例：123456:AAxxToken 或 bot001,123456:AAxxToken 或 bot001|123456:AAxxToken|my_bot|机器人昵称|10001') }}</p>
      </Form>
    </Modal>
  </div>
</template>
