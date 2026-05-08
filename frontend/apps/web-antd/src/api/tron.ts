const API_BASE = import.meta.env.VITE_TRON_API_URL || 'http://127.0.0.1:18001/api';

export interface ListResult<T = Record<string, any>> {
  count: number;
  next?: string | null;
  previous?: string | null;
  results: T[];
}

export interface ResourceConfig {
  endpoint: string;
  title: string;
  description?: string;
  columns: Array<{ dataIndex: string; title: string; ellipsis?: boolean }>;
  fields: Array<{ name: string; label: string; type?: 'boolean' | 'number' | 'textarea' | 'text' }>;
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const url = path.startsWith('http') ? path : `${API_BASE}${path}`;
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    ...options,
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `HTTP ${response.status}`);
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export function getDashboard() {
  return request<Record<string, number>>('/dashboard/');
}

export async function listResource<T = Record<string, any>>(endpoint: string, params: Record<string, any> = {}) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') search.set(key, String(value));
  });
  const suffix = search.toString() ? `?${search.toString()}` : '';
  const data = await request<ListResult<T> | T[]>(`${endpoint}/${suffix}`);
  if (Array.isArray(data)) return { count: data.length, results: data } as ListResult<T>;
  return data;
}

export function createResource(endpoint: string, data: Record<string, any>) {
  return request(`${endpoint}/`, { method: 'POST', body: JSON.stringify(data) });
}

export function updateResource(endpoint: string, id: string | number, data: Record<string, any>) {
  return request(`${endpoint}/${id}/`, { method: 'PATCH', body: JSON.stringify(data) });
}

export function deleteResource(endpoint: string, id: string | number) {
  return request(`${endpoint}/${id}/`, { method: 'DELETE' });
}

export async function getSingleton(endpoint: string, defaults: Record<string, any> = {}) {
  const list = await listResource(endpoint, { page_size: 1 });
  return list.results[0] || defaults;
}

export async function saveSingleton(endpoint: string, data: Record<string, any>) {
  if (data.id) return updateResource(endpoint, data.id, data);
  return createResource(endpoint, data);
}

export const resourceConfigs: Record<string, ResourceConfig> = {
  bots: {
    title: '机器人管理', endpoint: '/bots', description: 'Telegram Bot Token、Webhook、群组播报配置',
    columns: [
      { title: '机器人ID', dataIndex: 'robot_id' }, { title: '用户名', dataIndex: 'username' }, { title: '昵称', dataIndex: 'first_name' }, { title: '归属用户', dataIndex: 'owner_user_id' }, { title: 'Webhook', dataIndex: 'webhook_enabled' }, { title: '播报', dataIndex: 'broadcast_enabled' },
    ],
    fields: [
      { label: '机器人ID', name: 'robot_id' }, { label: 'Token', name: 'token' }, { label: '用户名', name: 'username' }, { label: '昵称', name: 'first_name' }, { label: '归属用户ID', name: 'owner_user_id' }, { label: '启用Webhook', name: 'webhook_enabled', type: 'boolean' }, { label: '启用群组播报', name: 'broadcast_enabled', type: 'boolean' },
    ],
  },
  promotions: {
    title: '推广文案', endpoint: '/promotions', description: '机器人命令、消息文案、按钮和自动回复',
    columns: [{ title: '标题', dataIndex: 'title' }, { title: '命令', dataIndex: 'command' }, { title: '类型', dataIndex: 'type' }, { title: '位置', dataIndex: 'position' }, { title: '排序', dataIndex: 'sort' }],
    fields: [{ label: '机器人ID', name: 'bot', type: 'number' }, { label: '标题', name: 'title' }, { label: '命令', name: 'command' }, { label: '内容', name: 'content', type: 'textarea' }, { label: '链接', name: 'url' }, { label: '回调内容', name: 'callback_data' }, { label: '类型', name: 'type' }, { label: '位置', name: 'position' }, { label: '自动回复', name: 'auto_reply', type: 'boolean' }, { label: '排序', name: 'sort', type: 'number' }],
  },

  botGroups: {
    title: '群组管理', endpoint: '/bot-groups', description: 'Telegram 群组绑定和收益播报开关',
    columns: [{ title: '群组ID', dataIndex: 'chat_id' }, { title: '群组名称', dataIndex: 'title' }, { title: '机器人ID', dataIndex: 'bot' }, { title: '收益播报', dataIndex: 'broadcast_enabled' }],
    fields: [{ label: '机器人ID', name: 'bot', type: 'number' }, { label: '群组ID', name: 'chat_id' }, { label: '群组名称', name: 'title' }, { label: '开启收益播报', name: 'broadcast_enabled', type: 'boolean' }],
  },
  addresses: {
    title: '地址池', endpoint: '/addresses', description: '兑换、能量、会员、监听地址统一管理',
    columns: [{ title: '地址', dataIndex: 'address' }, { title: '类型', dataIndex: 'address_type' }, { title: '用户ID', dataIndex: 'user_id' }, { title: '用户名', dataIndex: 'username' }, { title: '机器人', dataIndex: 'bot_id' }, { title: '已分配', dataIndex: 'allocated' }],
    fields: [{ label: '地址', name: 'address' }, { label: '私钥/密文', name: 'private_key_encrypted', type: 'textarea' }, { label: '地址类型', name: 'address_type' }, { label: '用户ID', name: 'user_id' }, { label: '用户名', name: 'username' }, { label: '机器人ID', name: 'bot_id' }, { label: '已分配', name: 'allocated', type: 'boolean' }],
  },
  exchangeOrders: {
    title: '兑换订单', endpoint: '/exchange/orders', description: 'TRX/USDT 兑换订单和出款状态',
    columns: [{ title: '订单号', dataIndex: 'order_no' }, { title: '用户ID', dataIndex: 'user_id' }, { title: '地址', dataIndex: 'address' }, { title: '金额', dataIndex: 'amount' }, { title: '返还金额', dataIndex: 'return_amount' }, { title: '类型', dataIndex: 'type' }, { title: '状态', dataIndex: 'status' }, { title: '利润USDT', dataIndex: 'profit_usdt' }],
    fields: [{ label: '订单号', name: 'order_no' }, { label: '机器人ID', name: 'bot_id' }, { label: '用户ID', name: 'user_id' }, { label: '地址', name: 'address' }, { label: '金额', name: 'amount', type: 'number' }, { label: '返还金额', name: 'return_amount', type: 'number' }, { label: '类型', name: 'type' }, { label: '状态', name: 'status' }, { label: '支付Hash', name: 'pay_txid' }, { label: '出款Hash', name: 'payout_txid' }, { label: '利润USDT', name: 'profit_usdt', type: 'number' }],
  },
  exchangeBlacklist: {
    title: '兑换黑名单', endpoint: '/exchange/blacklist', description: '禁止兑换地址',
    columns: [{ title: '地址', dataIndex: 'address' }, { title: '原因', dataIndex: 'reason' }],
    fields: [{ label: '地址', name: 'address' }, { label: '原因', name: 'reason', type: 'textarea' }],
  },
  energyPlans: {
    title: '能量套餐', endpoint: '/energy/plans', description: '闪租、时长、笔数、智能托管套餐',
    columns: [{ title: '名称', dataIndex: 'name' }, { title: '模式', dataIndex: 'mode' }, { title: '能量', dataIndex: 'energy_amount' }, { title: '小时', dataIndex: 'duration_hours' }, { title: '笔数', dataIndex: 'number_of_times' }, { title: 'TRX价格', dataIndex: 'price_trx' }, { title: 'USDT价格', dataIndex: 'price_usdt' }],
    fields: [{ label: '机器人ID', name: 'bot_id' }, { label: '名称', name: 'name' }, { label: '模式', name: 'mode' }, { label: '能量', name: 'energy_amount', type: 'number' }, { label: '小时', name: 'duration_hours', type: 'number' }, { label: '笔数', name: 'number_of_times', type: 'number' }, { label: 'TRX价格', name: 'price_trx', type: 'number' }, { label: 'USDT价格', name: 'price_usdt', type: 'number' }, { label: '排序', name: 'sort', type: 'number' }],
  },
  energyOrders: {
    title: '能量订单', endpoint: '/energy/orders', description: '能量闪租/代理委托订单',
    columns: [{ title: '订单号', dataIndex: 'order_no' }, { title: '用户ID', dataIndex: 'user_id' }, { title: '接收地址', dataIndex: 'receiver_address' }, { title: '能量', dataIndex: 'energy_amount' }, { title: 'TRX', dataIndex: 'trx_amount' }, { title: 'USDT', dataIndex: 'usdt_amount' }, { title: '状态', dataIndex: 'status' }],
    fields: [{ label: '订单号', name: 'order_no' }, { label: '机器人ID', name: 'bot_id' }, { label: '用户ID', name: 'user_id' }, { label: '接收地址', name: 'receiver_address' }, { label: '套餐ID', name: 'plan', type: 'number' }, { label: '能量', name: 'energy_amount', type: 'number' }, { label: 'TRX金额', name: 'trx_amount', type: 'number' }, { label: 'USDT金额', name: 'usdt_amount', type: 'number' }, { label: '支付方式', name: 'pay_type' }, { label: '状态', name: 'status' }, { label: '支付Hash', name: 'pay_txid' }, { label: '能量Hash', name: 'energy_txid' }, { label: '平台订单ID', name: 'platform_order_id' }],
  },
  memberGoods: {
    title: '会员商品', endpoint: '/membership/goods', description: '会员套餐、费率区间',
    columns: [{ title: '名称', dataIndex: 'name' }, { title: '天数', dataIndex: 'duration_days' }, { title: '售价', dataIndex: 'sell_amount' }, { title: '最小限额', dataIndex: 'min_limit' }, { title: '最大限额', dataIndex: 'max_limit' }],
    fields: [{ label: '名称', name: 'name' }, { label: '天数', name: 'duration_days', type: 'number' }, { label: '售价', name: 'sell_amount', type: 'number' }, { label: '最小限额', name: 'min_limit', type: 'number' }, { label: '最大限额', name: 'max_limit', type: 'number' }],
  },
  memberOrders: {
    title: '会员订单', endpoint: '/membership/orders', description: '会员购买和开通记录',
    columns: [{ title: '订单号', dataIndex: 'order_no' }, { title: '用户ID', dataIndex: 'user_id' }, { title: '目标用户', dataIndex: 'target_user_id' }, { title: '商品ID', dataIndex: 'goods' }, { title: '金额', dataIndex: 'amount' }, { title: '状态', dataIndex: 'status' }],
    fields: [{ label: '订单号', name: 'order_no' }, { label: '用户ID', name: 'user_id' }, { label: '目标用户ID', name: 'target_user_id' }, { label: '商品ID', name: 'goods', type: 'number' }, { label: '支付类型', name: 'pay_type' }, { label: '金额', name: 'amount', type: 'number' }, { label: '交易Hash', name: 'txid' }, { label: '状态', name: 'status' }],
  },
  balances: {
    title: '用户余额', endpoint: '/finance/balances', description: 'TRX、USDT、积分余额',
    columns: [{ title: '用户ID', dataIndex: 'user_id' }, { title: '机器人', dataIndex: 'bot_id' }, { title: 'TRX', dataIndex: 'trx' }, { title: 'USDT', dataIndex: 'usdt' }, { title: '积分', dataIndex: 'integral' }],
    fields: [{ label: '用户ID', name: 'user_id' }, { label: '机器人ID', name: 'bot_id' }, { label: 'TRX', name: 'trx', type: 'number' }, { label: 'USDT', name: 'usdt', type: 'number' }, { label: '积分', name: 'integral', type: 'number' }],
  },
  runningWater: {
    title: '资金流水', endpoint: '/finance/running-water', description: '充值、兑换、能量、会员、提现流水',
    columns: [{ title: '用户ID', dataIndex: 'user_id' }, { title: '业务类型', dataIndex: 'business_type' }, { title: '金额', dataIndex: 'amount' }, { title: '币种', dataIndex: 'token_type' }, { title: '变更前', dataIndex: 'before_balance' }, { title: '变更后', dataIndex: 'after_balance' }, { title: '关联单号', dataIndex: 'ref_no' }],
    fields: [{ label: '用户ID', name: 'user_id' }, { label: '机器人ID', name: 'bot_id' }, { label: '业务类型', name: 'business_type' }, { label: '金额', name: 'amount', type: 'number' }, { label: '币种', name: 'token_type' }, { label: '变更前', name: 'before_balance', type: 'number' }, { label: '变更后', name: 'after_balance', type: 'number' }, { label: '关联单号', name: 'ref_no' }],
  },
  withdrawals: {
    title: '提现审核', endpoint: '/finance/withdrawals', description: '用户提现审批和打款',
    columns: [{ title: '用户ID', dataIndex: 'user_id' }, { title: '地址', dataIndex: 'address' }, { title: '金额', dataIndex: 'amount' }, { title: '币种', dataIndex: 'token_type' }, { title: '状态', dataIndex: 'status' }, { title: 'Hash', dataIndex: 'txid' }],
    fields: [{ label: '用户ID', name: 'user_id' }, { label: '地址', name: 'address' }, { label: '金额', name: 'amount', type: 'number' }, { label: '币种', name: 'token_type' }, { label: '状态', name: 'status' }, { label: '交易Hash', name: 'txid' }, { label: '审核人', name: 'reviewed_by' }],
  },
};
