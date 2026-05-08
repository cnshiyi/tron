<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { Card, Col, Row, Statistic, Alert } from 'ant-design-vue';
import { getDashboard } from '#/api/tron';

const loading = ref(false);
const error = ref('');
const stats = ref<Record<string, number>>({});
const cards = [
  ['bots', '机器人'],
  ['exchange_orders', '兑换订单'],
  ['energy_orders', '能量订单'],
  ['balances', '余额账户'],
  ['pending_withdrawals', '待审核提现'],
];

async function load() {
  loading.value = true;
  error.value = '';
  try { stats.value = await getDashboard(); }
  catch (e: any) { error.value = e.message || String(e); }
  finally { loading.value = false; }
}

onMounted(load);
</script>

<template>
  <div class="p-5">
    <Alert v-if="error" class="mb-4" type="error" :message="error" show-icon />
    <Row :gutter="16">
      <Col v-for="item in cards" :key="item[0]" :xs="24" :md="8" :xl="4">
        <Card class="mb-4" :loading="loading">
          <Statistic :title="item[1]" :value="stats[item[0]] || 0" />
        </Card>
      </Col>
    </Row>
    <Card title="TRON 能量机器人后台">
      <p>已迁移旧系统的机器人、兑换、能量、会员、资金、地址池等核心管理入口，前端继续使用 vue-vben-admin。</p>
      <p>左侧菜单进入各模块，可直接通过 Django API 增删改查。</p>
    </Card>
  </div>
</template>
