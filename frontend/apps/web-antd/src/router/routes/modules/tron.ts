import type { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    name: 'Tron',
    path: '/tron',
    redirect: '/tron/dashboard',
    meta: { icon: 'cryptocurrency-color:trx', order: -10, title: 'TRON后台' },
    children: [
      { name: 'TronDashboard', path: '/tron/dashboard', component: () => import('#/views/tron/Dashboard.vue'), meta: { affixTab: true, icon: 'lucide:layout-dashboard', title: '控制台' } },
      { name: 'TronSettings', path: '/tron/settings', component: () => import('#/views/tron/Settings.vue'), meta: { icon: 'lucide:settings', title: '系统配置' } },
      { name: 'TronBots', path: '/tron/resource/bots', component: () => import('#/views/tron/ResourcePage.vue'), meta: { icon: 'lucide:bot', title: '机器人管理' }, props: { key: 'bots' } },
      { name: 'TronPromotions', path: '/tron/resource/promotions', component: () => import('#/views/tron/ResourcePage.vue'), meta: { icon: 'lucide:megaphone', title: '推广文案' }, props: { key: 'promotions' } },
      { name: 'TronBotGroups', path: '/tron/resource/botGroups', component: () => import('#/views/tron/ResourcePage.vue'), meta: { icon: 'lucide:users', title: '群组管理' }, props: { key: 'botGroups' } },
      { name: 'TronAddresses', path: '/tron/resource/addresses', component: () => import('#/views/tron/ResourcePage.vue'), meta: { icon: 'lucide:wallet-cards', title: '地址池' }, props: { key: 'addresses' } },
      { name: 'TronExchangeOrders', path: '/tron/resource/exchangeOrders', component: () => import('#/views/tron/ResourcePage.vue'), meta: { icon: 'lucide:refresh-cw', title: '兑换订单' }, props: { key: 'exchangeOrders' } },
      { name: 'TronExchangeBlacklist', path: '/tron/resource/exchangeBlacklist', component: () => import('#/views/tron/ResourcePage.vue'), meta: { icon: 'lucide:ban', title: '兑换黑名单' }, props: { key: 'exchangeBlacklist' } },
      { name: 'TronEnergyPlans', path: '/tron/resource/energyPlans', component: () => import('#/views/tron/ResourcePage.vue'), meta: { icon: 'lucide:zap', title: '能量套餐' }, props: { key: 'energyPlans' } },
      { name: 'TronEnergyOrders', path: '/tron/resource/energyOrders', component: () => import('#/views/tron/ResourcePage.vue'), meta: { icon: 'lucide:bolt', title: '能量订单' }, props: { key: 'energyOrders' } },
      { name: 'TronMemberGoods', path: '/tron/resource/memberGoods', component: () => import('#/views/tron/ResourcePage.vue'), meta: { icon: 'lucide:badge-vip', title: '会员商品' }, props: { key: 'memberGoods' } },
      { name: 'TronMemberOrders', path: '/tron/resource/memberOrders', component: () => import('#/views/tron/ResourcePage.vue'), meta: { icon: 'lucide:shopping-bag', title: '会员订单' }, props: { key: 'memberOrders' } },
      { name: 'TronBalances', path: '/tron/resource/balances', component: () => import('#/views/tron/ResourcePage.vue'), meta: { icon: 'lucide:circle-dollar-sign', title: '用户余额' }, props: { key: 'balances' } },
      { name: 'TronRunningWater', path: '/tron/resource/runningWater', component: () => import('#/views/tron/ResourcePage.vue'), meta: { icon: 'lucide:list', title: '资金流水' }, props: { key: 'runningWater' } },
      { name: 'TronWithdrawals', path: '/tron/resource/withdrawals', component: () => import('#/views/tron/ResourcePage.vue'), meta: { icon: 'lucide:banknote-arrow-up', title: '提现审核' }, props: { key: 'withdrawals' } },
    ],
  },
];

export default routes;
