<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';
import { Button, Card, Col, Form, FormItem, Input, InputNumber, Row, Switch, Textarea, message } from 'ant-design-vue';
import { getDefaultTextConfigs, getSingleton, loadUiText, saveSingleton, syncTextDefaults, uiText } from '#/api/tron';

const loading = ref(false);
const textSyncing = ref(false);
const t = uiText;
const exchange = reactive<Record<string, any>>({});
const hourly = reactive<Record<string, any>>({ name: '3.2W 能量闪租', mode: 'hourly', energy_amount: 32000, duration_hours: 1 });

async function load() {
  loading.value = true;
  try {
    Object.assign(exchange, await getSingleton('/exchange/configs', { auto_mode: true }));
    Object.assign(hourly, await getSingleton('/energy/plans', hourly));
  } catch (e: any) { message.error(e.message || String(e)); }
  finally { loading.value = false; }
}

async function saveAll() {
  loading.value = true;
  try {
    await saveSingleton('/exchange/configs', exchange);
    const energyPayload = { ...hourly };
    delete energyPayload.description;
    await saveSingleton('/energy/plans', energyPayload);
    message.success(t('settings.saved', '配置已保存'));
    await load();
  } catch (e: any) { message.error(e.message || String(e)); }
  finally { loading.value = false; }
}

async function syncTexts() {
  textSyncing.value = true;
  try {
    const result = await syncTextDefaults(getDefaultTextConfigs());
    await loadUiText(true);
    message.success(t('settings.sync_success_template', '文字配置已同步：新增 {created} 项，更新 {updated} 项')
      .replace('{created}', String(result.created))
      .replace('{updated}', String(result.updated)));
  } catch (e: any) { message.error(e.message || String(e)); }
  finally { textSyncing.value = false; }
}

onMounted(async () => {
  await loadUiText().catch(() => undefined);
  await load();
});
</script>

<template>
  <div class="p-5">
    <Card :title="t('settings.title', '系统配置')" :loading="loading">
      <Form layout="vertical">
        <h3 class="mb-3 text-lg">{{ t('settings.exchange_title', '汇率配置') }}</h3>
        <Row :gutter="16">
          <Col :span="8"><FormItem label="机器人ID"><Input v-model:value="exchange.bot_id" /></FormItem></Col>
          <Col :span="8"><FormItem label="U兑换TRX汇率"><InputNumber v-model:value="exchange.usdt_to_trx_rate" class="w-full" /></FormItem></Col>
          <Col :span="8"><FormItem label="TRX兑换USDT汇率"><InputNumber v-model:value="exchange.trx_to_usdt_rate" class="w-full" /></FormItem></Col>
          <Col :span="8"><FormItem label="上浮费率"><InputNumber v-model:value="exchange.float_rate" class="w-full" /></FormItem></Col>
          <Col :span="8"><FormItem label="最小限额"><InputNumber v-model:value="exchange.min_limit" class="w-full" /></FormItem></Col>
          <Col :span="8"><FormItem label="最大限额"><InputNumber v-model:value="exchange.max_limit" class="w-full" /></FormItem></Col>
          <Col :span="8"><FormItem label="自动模式"><Switch v-model:checked="exchange.auto_mode" /></FormItem></Col>
        </Row>
        <h3 class="mb-3 mt-5 text-lg">{{ t('settings.energy_title', '能量闪租配置') }}</h3>
        <Row :gutter="16">
          <Col :span="8"><FormItem label="套餐名称"><Input v-model:value="hourly.name" /></FormItem></Col>
          <Col :span="8"><FormItem label="模式"><Input v-model:value="hourly.mode" /></FormItem></Col>
          <Col :span="8"><FormItem label="能量数量"><InputNumber v-model:value="hourly.energy_amount" class="w-full" /></FormItem></Col>
          <Col :span="8"><FormItem label="时长(小时)"><InputNumber v-model:value="hourly.duration_hours" class="w-full" /></FormItem></Col>
          <Col :span="8"><FormItem label="TRX价格"><InputNumber v-model:value="hourly.price_trx" class="w-full" /></FormItem></Col>
          <Col :span="8"><FormItem label="USDT价格"><InputNumber v-model:value="hourly.price_usdt" class="w-full" /></FormItem></Col>
          <Col :span="24"><FormItem label="说明文本"><Textarea v-model:value="hourly.description" :rows="4" placeholder="旧前端中的文本内容可放这里，后续可对接机器人展示" /></FormItem></Col>
        </Row>
        <Button type="primary" @click="saveAll">{{ t('settings.save', '保存配置') }}</Button>
        <Button class="ml-2" :loading="textSyncing" @click="syncTexts">{{ t('settings.sync_text', '同步默认文字配置') }}</Button>
      </Form>
    </Card>
  </div>
</template>
