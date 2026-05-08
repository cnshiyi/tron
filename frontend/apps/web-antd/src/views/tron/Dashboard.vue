<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { Alert, Card, Col, Row, Statistic, Table } from 'ant-design-vue';
import { getDashboard, getReportOverview, loadUiText, uiText } from '#/api/tron';

const loading = ref(false);
const error = ref('');
const stats = ref<Record<string, number>>({});
const report = ref<Record<string, any>>({ summary: {}, status: {}, daily: {}, tokens: [] });

const textVersion = ref(0);
const t = uiText;

const cards = computed(() => {
  textVersion.value;
  return [
  ['bots', t('dashboard.card.bots', '机器人')],
  ['bot_groups', t('dashboard.card.bot_groups', '群组')],
  ['users', t('dashboard.card.users', '用户')],
  ['blacklisted_users', t('dashboard.card.blacklisted_users', '拉黑用户')],
  ['exchange_orders', t('dashboard.card.exchange_orders', '兑换订单')],
  ['energy_orders', t('dashboard.card.energy_orders', '能量订单')],
  ['member_orders', t('dashboard.card.member_orders', '会员订单')],
  ['balances', t('dashboard.card.balances', '余额账户')],
  ['listen_addresses', t('dashboard.card.listen_addresses', '监听地址')],
  ['pending_withdrawals', t('dashboard.card.pending_withdrawals', '待审核提现')],
];
});

const summaryCards = computed(() => {
  textVersion.value;
  return [
  ['exchange_amount', t('dashboard.summary.exchange_amount', '兑换成交金额')],
  ['exchange_return_amount', t('dashboard.summary.exchange_return_amount', '兑换返还金额')],
  ['exchange_profit_usdt', t('dashboard.summary.exchange_profit_usdt', '兑换利润 USDT')],
  ['energy_trx_amount', t('dashboard.summary.energy_trx_amount', '能量收入 TRX')],
  ['energy_usdt_amount', t('dashboard.summary.energy_usdt_amount', '能量收入 USDT')],
  ['member_amount', t('dashboard.summary.member_amount', '会员订单金额')],
  ['member_recharge_amount', t('dashboard.summary.member_recharge_amount', '会员充值金额')],
  ['commission_amount', t('dashboard.summary.commission_amount', '已结算佣金')],
  ['withdrawal_paid_amount', t('dashboard.summary.withdrawal_paid_amount', '已打款提现')],
  ['running_water_amount', t('dashboard.summary.running_water_amount', '流水总额')],
];
});

const statusColumns = computed(() => {
  textVersion.value;
  return [
  { title: t('dashboard.column.status', '状态'), dataIndex: 'status' },
  { title: t('dashboard.column.count', '数量'), dataIndex: 'count' },
];
});

const tokenColumns = computed(() => {
  textVersion.value;
  return [
  { title: t('dashboard.column.token_type', '币种'), dataIndex: 'token_type' },
  { title: t('dashboard.column.times', '笔数'), dataIndex: 'count' },
  { title: t('dashboard.column.amount', '金额'), dataIndex: 'amount' },
];
});

const dailyColumns = computed(() => {
  textVersion.value;
  return [
  { title: t('dashboard.column.date', '日期'), dataIndex: 'date' },
  { title: t('dashboard.column.times', '笔数'), dataIndex: 'count' },
  { title: t('dashboard.column.amount', '金额'), dataIndex: 'amount' },
];
});

function statusRows(key: string) {
  return (report.value.status?.[key] || []).map((item: any, index: number) => ({ id: `${key}-${index}`, ...item }));
}

function dailyRows(key: string) {
  return (report.value.daily?.[key] || []).map((item: any, index: number) => ({ id: `${key}-${index}`, ...item }));
}

async function load() {
  textVersion.value;
  loading.value = true;
  error.value = '';
  try {
    const [dashboardData, reportData] = await Promise.all([getDashboard(), getReportOverview()]);
    stats.value = dashboardData;
    report.value = reportData;
  } catch (e: any) {
    error.value = e.message || String(e);
  } finally {
    loading.value = false;
  }
}

onMounted(async () => {
  await loadUiText().catch(() => undefined);
  textVersion.value += 1;
  await load();
});
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

    <Card class="mb-4" :title="t('dashboard.summary_title', '收益/资金汇总')">
      <Row :gutter="16">
        <Col v-for="item in summaryCards" :key="item[0]" :xs="24" :md="8" :xl="6">
          <Statistic class="mb-4" :title="item[1]" :precision="2" :value="Number(report.summary?.[item[0]] || 0)" />
        </Col>
      </Row>
    </Card>

    <Row :gutter="16">
      <Col :xs="24" :xl="12">
        <Card class="mb-4" :title="t('dashboard.exchange_status_title', '兑换订单状态')">
          <Table row-key="id" size="small" :columns="statusColumns" :data-source="statusRows('exchange_orders')" :pagination="false" />
        </Card>
      </Col>
      <Col :xs="24" :xl="12">
        <Card class="mb-4" :title="t('dashboard.energy_status_title', '能量订单状态')">
          <Table row-key="id" size="small" :columns="statusColumns" :data-source="statusRows('energy_orders')" :pagination="false" />
        </Card>
      </Col>
      <Col :xs="24" :xl="12">
        <Card class="mb-4" :title="t('dashboard.member_status_title', '会员订单状态')">
          <Table row-key="id" size="small" :columns="statusColumns" :data-source="statusRows('member_orders')" :pagination="false" />
        </Card>
      </Col>
      <Col :xs="24" :xl="12">
        <Card class="mb-4" :title="t('dashboard.withdrawal_status_title', '提现状态')">
          <Table row-key="id" size="small" :columns="statusColumns" :data-source="statusRows('withdrawals')" :pagination="false" />
        </Card>
      </Col>
    </Row>

    <Row :gutter="16">
      <Col :xs="24" :xl="12">
        <Card class="mb-4" :title="t('dashboard.token_summary_title', '资金流水币种汇总')">
          <Table row-key="token_type" size="small" :columns="tokenColumns" :data-source="report.tokens || []" :pagination="false" />
        </Card>
      </Col>
      <Col :xs="24" :xl="12">
        <Card class="mb-4" :title="t('dashboard.exchange_daily_title', '近 14 天兑换金额')">
          <Table row-key="id" size="small" :columns="dailyColumns" :data-source="dailyRows('exchange')" :pagination="false" />
        </Card>
      </Col>
    </Row>

    <Card :title="t('dashboard.title', 'TRON 能量机器人后台')">
      <p>{{ t('dashboard.description_1', '已迁移旧系统的机器人、兑换、能量、会员、资金、地址池等核心管理入口，前端继续使用 vue-vben-admin。') }}</p>
      <p>{{ t('dashboard.description_2', '控制台已接入统计报表：用户、订单、收益、佣金、兑换、能量、会员、提现和资金流水。') }}</p>
    </Card>
  </div>
</template>
