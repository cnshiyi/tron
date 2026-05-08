<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { Alert, Card, Col, Row, Statistic, Table } from 'ant-design-vue';
import { getDashboard, getReportOverview } from '#/api/tron';

const loading = ref(false);
const error = ref('');
const stats = ref<Record<string, number>>({});
const report = ref<Record<string, any>>({ summary: {}, status: {}, daily: {}, tokens: [] });

const cards = [
  ['bots', '机器人'],
  ['bot_groups', '群组'],
  ['users', '用户'],
  ['blacklisted_users', '拉黑用户'],
  ['exchange_orders', '兑换订单'],
  ['energy_orders', '能量订单'],
  ['member_orders', '会员订单'],
  ['balances', '余额账户'],
  ['listen_addresses', '监听地址'],
  ['pending_withdrawals', '待审核提现'],
];

const summaryCards = [
  ['exchange_amount', '兑换成交金额'],
  ['exchange_return_amount', '兑换返还金额'],
  ['exchange_profit_usdt', '兑换利润 USDT'],
  ['energy_trx_amount', '能量收入 TRX'],
  ['energy_usdt_amount', '能量收入 USDT'],
  ['member_amount', '会员订单金额'],
  ['member_recharge_amount', '会员充值金额'],
  ['commission_amount', '已结算佣金'],
  ['withdrawal_paid_amount', '已打款提现'],
  ['running_water_amount', '流水总额'],
];

const statusColumns = [
  { title: '状态', dataIndex: 'status' },
  { title: '数量', dataIndex: 'count' },
];

const tokenColumns = [
  { title: '币种', dataIndex: 'token_type' },
  { title: '笔数', dataIndex: 'count' },
  { title: '金额', dataIndex: 'amount' },
];

const dailyColumns = [
  { title: '日期', dataIndex: 'date' },
  { title: '笔数', dataIndex: 'count' },
  { title: '金额', dataIndex: 'amount' },
];

function statusRows(key: string) {
  return (report.value.status?.[key] || []).map((item: any, index: number) => ({ id: `${key}-${index}`, ...item }));
}

function dailyRows(key: string) {
  return (report.value.daily?.[key] || []).map((item: any, index: number) => ({ id: `${key}-${index}`, ...item }));
}

async function load() {
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

    <Card class="mb-4" title="收益/资金汇总">
      <Row :gutter="16">
        <Col v-for="item in summaryCards" :key="item[0]" :xs="24" :md="8" :xl="6">
          <Statistic class="mb-4" :title="item[1]" :precision="2" :value="Number(report.summary?.[item[0]] || 0)" />
        </Col>
      </Row>
    </Card>

    <Row :gutter="16">
      <Col :xs="24" :xl="12">
        <Card class="mb-4" title="兑换订单状态">
          <Table row-key="id" size="small" :columns="statusColumns" :data-source="statusRows('exchange_orders')" :pagination="false" />
        </Card>
      </Col>
      <Col :xs="24" :xl="12">
        <Card class="mb-4" title="能量订单状态">
          <Table row-key="id" size="small" :columns="statusColumns" :data-source="statusRows('energy_orders')" :pagination="false" />
        </Card>
      </Col>
      <Col :xs="24" :xl="12">
        <Card class="mb-4" title="会员订单状态">
          <Table row-key="id" size="small" :columns="statusColumns" :data-source="statusRows('member_orders')" :pagination="false" />
        </Card>
      </Col>
      <Col :xs="24" :xl="12">
        <Card class="mb-4" title="提现状态">
          <Table row-key="id" size="small" :columns="statusColumns" :data-source="statusRows('withdrawals')" :pagination="false" />
        </Card>
      </Col>
    </Row>

    <Row :gutter="16">
      <Col :xs="24" :xl="12">
        <Card class="mb-4" title="资金流水币种汇总">
          <Table row-key="token_type" size="small" :columns="tokenColumns" :data-source="report.tokens || []" :pagination="false" />
        </Card>
      </Col>
      <Col :xs="24" :xl="12">
        <Card class="mb-4" title="近 14 天兑换金额">
          <Table row-key="id" size="small" :columns="dailyColumns" :data-source="dailyRows('exchange')" :pagination="false" />
        </Card>
      </Col>
    </Row>

    <Card title="TRON 能量机器人后台">
      <p>已迁移旧系统的机器人、兑换、能量、会员、资金、地址池等核心管理入口，前端继续使用 vue-vben-admin。</p>
      <p>控制台已接入统计报表：用户、订单、收益、佣金、兑换、能量、会员、提现和资金流水。</p>
    </Card>
  </div>
</template>
