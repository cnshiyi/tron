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
  actions?: Array<{ name: string; label: string; path: string; danger?: boolean; confirm?: string; promptField?: string; promptLabel?: string; payload?: Record<string, any> }>;
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

export function getReportOverview() {
  return request<Record<string, any>>('/reports/overview/');
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

export function actionResource(endpoint: string, id: string | number, path: string, data: Record<string, any> = {}) {
  return request(`${endpoint}/${id}/${path}/`, { method: 'POST', body: JSON.stringify(data) });
}

export function bulkCreateBots(data: {
  broadcast_enabled?: boolean;
  content: string;
  default_owner_user_id?: string;
  webhook_enabled?: boolean;
}) {
  return request<{ created_count: number; created: any[]; skipped: any[]; errors: any[] }>(
    '/bots/bulk-create/',
    { method: 'POST', body: JSON.stringify(data) },
  );
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
    actions: [
      { name: 'setWebhook', label: '设置Webhook', path: 'set-webhook', promptField: 'base_url', promptLabel: '请输入公网域名，如 https://example.com，留空则使用后端 PUBLIC_BASE_URL', payload: { dry_run: true } },
      { name: 'broadcast', label: '群发演练', path: 'broadcast', promptField: 'content', promptLabel: '请输入群发内容（默认演练，不真实发送）', payload: { dry_run: true } },
    ],
  },
  promotions: {
    title: '推广文案', endpoint: '/promotions', description: '机器人命令、消息文案、按钮和自动回复',
    columns: [{ title: '标题', dataIndex: 'title' }, { title: '命令', dataIndex: 'command' }, { title: '类型', dataIndex: 'type' }, { title: '位置', dataIndex: 'position' }, { title: '排序', dataIndex: 'sort' }],
    fields: [{ label: '机器人ID', name: 'bot', type: 'number' }, { label: '标题', name: 'title' }, { label: '命令', name: 'command' }, { label: '内容', name: 'content', type: 'textarea' }, { label: '链接', name: 'url' }, { label: '回调内容', name: 'callback_data' }, { label: '类型', name: 'type' }, { label: '位置', name: 'position' }, { label: '自动回复', name: 'auto_reply', type: 'boolean' }, { label: '排序', name: 'sort', type: 'number' }],
  },


  broadcastLogs: {
    title: '群发记录', endpoint: '/broadcast-logs', description: '机器人群发/收益播报发送结果和错误日志',
    columns: [{ title: '机器人', dataIndex: 'bot' }, { title: '群组', dataIndex: 'chat_id' }, { title: '标题', dataIndex: 'title' }, { title: '状态', dataIndex: 'status' }, { title: '消息ID', dataIndex: 'telegram_message_id' }, { title: '错误', dataIndex: 'error_message' }],
    fields: [{ label: '机器人ID', name: 'bot', type: 'number' }, { label: '群组ID', name: 'group', type: 'number' }, { label: 'Chat ID', name: 'chat_id' }, { label: '标题', name: 'title' }, { label: '内容', name: 'content', type: 'textarea' }, { label: '状态', name: 'status' }, { label: '消息ID', name: 'telegram_message_id' }, { label: '错误信息', name: 'error_message', type: 'textarea' }],
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
    actions: [
      { name: 'markPaid', label: '已支付', path: 'mark-paid', promptField: 'txid', promptLabel: '请输入支付 Hash' },
      { name: 'markSent', label: '已出款', path: 'mark-sent', promptField: 'txid', promptLabel: '请输入出款 Hash' },
      { name: 'fail', label: '失败', path: 'fail', danger: true, confirm: '确认标记失败？' },
      { name: 'cancel', label: '取消', path: 'cancel', danger: true, confirm: '确认取消订单？' },
    ],
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
    actions: [
      { name: 'markPaid', label: '已支付', path: 'mark-paid', promptField: 'txid', promptLabel: '请输入支付 Hash' },
      { name: 'delegating', label: '委托中', path: 'delegating', confirm: '确认标记委托中？' },
      { name: 'delegate', label: 'SOHU委托演练', path: 'delegate', payload: { dry_run: true, mode: 'smart' }, confirm: '确认发起 SOHU 能量委托演练？不会真实请求外部接口。' },
      { name: 'success', label: '成功', path: 'success', promptField: 'txid', promptLabel: '请输入能量交易 Hash' },
      { name: 'fail', label: '失败', path: 'fail', danger: true, confirm: '确认标记失败？' },
    ],
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
    actions: [
      { name: 'markPaid', label: '已支付', path: 'mark-paid', promptField: 'txid', promptLabel: '请输入支付 Hash，可留空' },
      { name: 'activate', label: '开通权益', path: 'activate', confirm: '确认开通会员权益并生成分佣？' },
      { name: 'cancel', label: '取消', path: 'cancel', danger: true, confirm: '确认取消订单？' },
    ],
  },
  balances: {
    title: '用户余额', endpoint: '/finance/balances', description: 'TRX、USDT、积分余额',
    columns: [{ title: '用户ID', dataIndex: 'user_id' }, { title: '机器人', dataIndex: 'bot_id' }, { title: 'TRX', dataIndex: 'trx' }, { title: 'USDT', dataIndex: 'usdt' }, { title: '积分', dataIndex: 'integral' }],
    fields: [{ label: '用户ID', name: 'user_id' }, { label: '机器人ID', name: 'bot_id' }, { label: 'TRX', name: 'trx', type: 'number' }, { label: 'USDT', name: 'usdt', type: 'number' }, { label: '积分', name: 'integral', type: 'number' }],
    actions: [
      { name: 'addUsdt', label: '+USDT', path: 'adjust', payload: { token_type: 'usdt', amount: '1', business_type: 'manual_add_usdt' }, confirm: '确认给该用户增加 1 USDT？' },
      { name: 'subUsdt', label: '-USDT', path: 'adjust', danger: true, payload: { token_type: 'usdt', amount: '-1', business_type: 'manual_sub_usdt' }, confirm: '确认扣减该用户 1 USDT？' },
    ],
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
    actions: [
      { name: 'approve', label: '通过', path: 'approve', payload: { reviewed_by: 'admin' }, confirm: '确认审核通过？' },
      { name: 'reject', label: '拒绝', path: 'reject', danger: true, payload: { reviewed_by: 'admin' }, confirm: '确认拒绝提现？' },
      { name: 'markPaid', label: '已打款', path: 'mark-paid', promptField: 'txid', promptLabel: '请输入打款交易 Hash', payload: { reviewed_by: 'admin' } },
      { name: 'payout', label: '打款演练', path: 'payout', payload: { dry_run: true, reviewed_by: 'admin' }, confirm: '确认执行提现打款演练？不会真实转账。' },
    ],
  },
  users: {
    title: '用户管理', endpoint: '/users', description: 'Telegram 用户、邀请关系、会员状态、拉黑/置顶',
    columns: [{ title: '用户ID', dataIndex: 'user_id' }, { title: '机器人', dataIndex: 'bot_id' }, { title: '用户名', dataIndex: 'username' }, { title: '昵称', dataIndex: 'first_name' }, { title: '邀请人', dataIndex: 'inviter_id' }, { title: '会员等级', dataIndex: 'member_level' }, { title: '拉黑', dataIndex: 'is_blacklisted' }, { title: '置顶', dataIndex: 'is_top' }],
    fields: [{ label: '用户ID', name: 'user_id' }, { label: '机器人ID', name: 'bot_id' }, { label: '用户名', name: 'username' }, { label: '昵称', name: 'first_name' }, { label: '邀请人ID', name: 'inviter_id' }, { label: '会员等级', name: 'member_level' }, { label: '拉黑', name: 'is_blacklisted', type: 'boolean' }, { label: '置顶', name: 'is_top', type: 'boolean' }, { label: '累计充值', name: 'total_recharge', type: 'number' }, { label: '累计消费', name: 'total_consumption', type: 'number' }],
    actions: [
      { name: 'blacklist', label: '拉黑', path: 'blacklist', danger: true, confirm: '确认拉黑该用户？' },
      { name: 'unblacklist', label: '取消拉黑', path: 'unblacklist', confirm: '确认取消拉黑？' },
      { name: 'top', label: '置顶', path: 'top', confirm: '确认置顶该用户？' },
      { name: 'untop', label: '取消置顶', path: 'untop', confirm: '确认取消置顶？' },
    ],
  },
  userTops: {
    title: '用户排行', endpoint: '/user-tops', description: '用户充值/消费排行快照',
    columns: [{ title: '排名', dataIndex: 'rank' }, { title: '用户ID', dataIndex: 'user_id' }, { title: '机器人', dataIndex: 'bot_id' }, { title: '排行类型', dataIndex: 'rank_type' }, { title: '金额', dataIndex: 'amount' }, { title: '日期', dataIndex: 'snapshot_date' }],
    fields: [{ label: '用户ID', name: 'user_id' }, { label: '机器人ID', name: 'bot_id' }, { label: '排行类型', name: 'rank_type' }, { label: '金额', name: 'amount', type: 'number' }, { label: '排名', name: 'rank', type: 'number' }, { label: '快照日期', name: 'snapshot_date' }],
  },
  listenAddresses: {
    title: '监听地址', endpoint: '/listen-addresses', description: '链上充值/兑换监听地址',
    columns: [{ title: '地址', dataIndex: 'address' }, { title: '标签', dataIndex: 'label' }, { title: '机器人', dataIndex: 'bot_id' }, { title: '币种', dataIndex: 'token_type' }, { title: '最小金额', dataIndex: 'min_amount' }, { title: '启用', dataIndex: 'enabled' }],
    fields: [{ label: '地址', name: 'address' }, { label: '标签', name: 'label' }, { label: '机器人ID', name: 'bot_id' }, { label: '币种', name: 'token_type' }, { label: '最小金额', name: 'min_amount', type: 'number' }, { label: '启用', name: 'enabled', type: 'boolean' }, { label: '最后扫描Hash', name: 'last_scanned_txid' }],
    actions: [
      { name: 'scanDry', label: '扫描', path: 'scan', payload: { apply: false, limit: 20 }, confirm: '确认扫描该地址最近交易？默认只入库不处理订单。' },
      { name: 'scanApply', label: '扫描并处理', path: 'scan', payload: { apply: true, limit: 20 }, confirm: '确认扫描并自动匹配充值/兑换订单？' },
    ],
  },
  transactions: {
    title: '链上交易', endpoint: '/transactions', description: 'TRX/USDT/能量链上交易记录',
    columns: [{ title: 'Hash', dataIndex: 'txid' }, { title: 'From', dataIndex: 'from_address' }, { title: 'To', dataIndex: 'to_address' }, { title: '金额', dataIndex: 'amount' }, { title: '币种', dataIndex: 'token_type' }, { title: '确认', dataIndex: 'confirmed' }, { title: '已处理', dataIndex: 'processed' }, { title: '业务', dataIndex: 'matched_business' }, { title: '单号', dataIndex: 'ref_no' }],
    fields: [{ label: 'Hash', name: 'txid' }, { label: 'From', name: 'from_address' }, { label: 'To', name: 'to_address' }, { label: '监听地址', name: 'listen_address' }, { label: '金额', name: 'amount', type: 'number' }, { label: '币种', name: 'token_type' }, { label: '确认', name: 'confirmed', type: 'boolean' }, { label: '已处理', name: 'processed', type: 'boolean' }, { label: '匹配业务', name: 'matched_business' }, { label: '关联单号', name: 'ref_no' }],
    actions: [
      { name: 'process', label: '处理匹配', path: 'process', confirm: '确认按金额/Hash 匹配并处理业务订单？' },
    ],
  },
  energyAgentRecords: {
    title: '能量代理记录', endpoint: '/energy/agent-records', description: '代理能量订单、成本与利润',
    columns: [{ title: '订单号', dataIndex: 'order_no' }, { title: '代理用户', dataIndex: 'agent_user_id' }, { title: '用户ID', dataIndex: 'user_id' }, { title: '接收地址', dataIndex: 'receiver_address' }, { title: '能量', dataIndex: 'energy_amount' }, { title: '利润TRX', dataIndex: 'profit_trx' }, { title: '状态', dataIndex: 'status' }],
    fields: [{ label: '订单号', name: 'order_no' }, { label: '机器人ID', name: 'bot_id' }, { label: '代理用户ID', name: 'agent_user_id' }, { label: '用户ID', name: 'user_id' }, { label: '接收地址', name: 'receiver_address' }, { label: '能量', name: 'energy_amount', type: 'number' }, { label: '成本TRX', name: 'cost_trx', type: 'number' }, { label: '利润TRX', name: 'profit_trx', type: 'number' }, { label: '状态', name: 'status' }, { label: '交易Hash', name: 'txid' }],
  },
  energyAdvanceRecords: {
    title: '预支记录', endpoint: '/energy/advance-records', description: '用户/代理预支审核记录',
    columns: [{ title: '用户ID', dataIndex: 'user_id' }, { title: '机器人', dataIndex: 'bot_id' }, { title: '金额', dataIndex: 'amount' }, { title: '币种', dataIndex: 'token_type' }, { title: '状态', dataIndex: 'status' }, { title: '审核人', dataIndex: 'reviewed_by' }],
    fields: [{ label: '用户ID', name: 'user_id' }, { label: '机器人ID', name: 'bot_id' }, { label: '金额', name: 'amount', type: 'number' }, { label: '币种', name: 'token_type' }, { label: '状态', name: 'status' }, { label: '原因', name: 'reason', type: 'textarea' }, { label: '审核人', name: 'reviewed_by' }],
    actions: [
      { name: 'approve', label: '通过', path: 'approve', payload: { reviewed_by: 'admin' }, confirm: '确认通过预支？' },
      { name: 'reject', label: '拒绝', path: 'reject', danger: true, payload: { reviewed_by: 'admin' }, confirm: '确认拒绝预支？' },
    ],
  },
  energyAddressConfigs: {
    title: '能量地址配置', endpoint: '/energy/address-configs', description: '笔数/智能托管/闪租地址池配置',
    columns: [{ title: '地址', dataIndex: 'address' }, { title: '机器人', dataIndex: 'bot_id' }, { title: '模式', dataIndex: 'mode' }, { title: '最大能量', dataIndex: 'max_energy' }, { title: '已用能量', dataIndex: 'used_energy' }, { title: '启用', dataIndex: 'enabled' }],
    fields: [{ label: '地址', name: 'address' }, { label: '私钥/密文', name: 'private_key_encrypted', type: 'textarea' }, { label: '机器人ID', name: 'bot_id' }, { label: '模式', name: 'mode' }, { label: '最大能量', name: 'max_energy', type: 'number' }, { label: '已用能量', name: 'used_energy', type: 'number' }, { label: '启用', name: 'enabled', type: 'boolean' }],
  },
  memberRecharges: {
    title: '会员充值', endpoint: '/membership/recharges', description: '会员/余额充值记录',
    columns: [{ title: '订单号', dataIndex: 'order_no' }, { title: '用户ID', dataIndex: 'user_id' }, { title: '机器人', dataIndex: 'bot_id' }, { title: '金额', dataIndex: 'amount' }, { title: '币种', dataIndex: 'token_type' }, { title: '状态', dataIndex: 'status' }, { title: 'Hash', dataIndex: 'txid' }],
    fields: [{ label: '订单号', name: 'order_no' }, { label: '用户ID', name: 'user_id' }, { label: '机器人ID', name: 'bot_id' }, { label: '金额', name: 'amount', type: 'number' }, { label: '币种', name: 'token_type' }, { label: 'Hash', name: 'txid' }, { label: '状态', name: 'status' }],
    actions: [
      { name: 'markPaid', label: '确认到账', path: 'mark-paid', promptField: 'txid', promptLabel: '请输入充值 Hash，可留空' },
    ],
  },
  memberActivities: {
    title: '会员活动', endpoint: '/membership/activities', description: '充值赠送、会员活动、奖励规则',
    columns: [{ title: '标题', dataIndex: 'title' }, { title: '机器人', dataIndex: 'bot_id' }, { title: '类型', dataIndex: 'activity_type' }, { title: '奖励', dataIndex: 'reward_amount' }, { title: '币种', dataIndex: 'reward_token' }, { title: '启用', dataIndex: 'enabled' }],
    fields: [{ label: '标题', name: 'title' }, { label: '机器人ID', name: 'bot_id' }, { label: '活动类型', name: 'activity_type' }, { label: '奖励金额', name: 'reward_amount', type: 'number' }, { label: '奖励币种', name: 'reward_token' }, { label: '开始时间', name: 'start_at' }, { label: '结束时间', name: 'end_at' }, { label: '启用', name: 'enabled', type: 'boolean' }, { label: '规则', name: 'rule', type: 'textarea' }],
  },
  memberCommissions: {
    title: '会员佣金', endpoint: '/membership/commissions', description: '邀请/会员分佣记录',
    columns: [{ title: '用户ID', dataIndex: 'user_id' }, { title: '邀请人', dataIndex: 'inviter_id' }, { title: '订单号', dataIndex: 'source_order_no' }, { title: '金额', dataIndex: 'amount' }, { title: '币种', dataIndex: 'token_type' }, { title: '状态', dataIndex: 'status' }],
    fields: [{ label: '用户ID', name: 'user_id' }, { label: '邀请人ID', name: 'inviter_id' }, { label: '机器人ID', name: 'bot_id' }, { label: '来源订单', name: 'source_order_no' }, { label: '金额', name: 'amount', type: 'number' }, { label: '币种', name: 'token_type' }, { label: '状态', name: 'status' }],
    actions: [
      { name: 'settle', label: '结算佣金', path: 'settle', payload: { reviewed_by: 'admin' }, confirm: '确认把佣金结算到邀请人余额？' },
    ],
  },
  energyHourlyTimes: {
    title: '能量时长配置', endpoint: '/energy/hourly-times', description: '闪租时长入口配置',
    columns: [{ title: '名称', dataIndex: 'name' }, { title: '机器人', dataIndex: 'bot_id' }, { title: '小时', dataIndex: 'hours' }, { title: '启用', dataIndex: 'enabled' }, { title: '排序', dataIndex: 'sort' }],
    fields: [{ label: '名称', name: 'name' }, { label: '机器人ID', name: 'bot_id' }, { label: '小时', name: 'hours', type: 'number' }, { label: '启用', name: 'enabled', type: 'boolean' }, { label: '排序', name: 'sort', type: 'number' }],
  },
  energyHourlyTimePrices: {
    title: '能量时长价格', endpoint: '/energy/hourly-time-prices', description: '不同能量/时长价格配置',
    columns: [{ title: '时长ID', dataIndex: 'time' }, { title: '机器人', dataIndex: 'bot_id' }, { title: '能量', dataIndex: 'energy_amount' }, { title: 'TRX价格', dataIndex: 'price_trx' }, { title: 'USDT价格', dataIndex: 'price_usdt' }, { title: '启用', dataIndex: 'enabled' }],
    fields: [{ label: '时长ID', name: 'time', type: 'number' }, { label: '机器人ID', name: 'bot_id' }, { label: '能量', name: 'energy_amount', type: 'number' }, { label: 'TRX价格', name: 'price_trx', type: 'number' }, { label: 'USDT价格', name: 'price_usdt', type: 'number' }, { label: '启用', name: 'enabled', type: 'boolean' }],
  },
  energyPenPlans: {
    title: '能量笔数套餐', endpoint: '/energy/pen-plans', description: '按笔数购买的能量套餐',
    columns: [{ title: '名称', dataIndex: 'name' }, { title: '机器人', dataIndex: 'bot_id' }, { title: '笔数', dataIndex: 'number_of_times' }, { title: '能量', dataIndex: 'energy_amount' }, { title: 'TRX价格', dataIndex: 'price_trx' }, { title: '启用', dataIndex: 'enabled' }],
    fields: [{ label: '名称', name: 'name' }, { label: '机器人ID', name: 'bot_id' }, { label: '笔数', name: 'number_of_times', type: 'number' }, { label: '能量', name: 'energy_amount', type: 'number' }, { label: 'TRX价格', name: 'price_trx', type: 'number' }, { label: 'USDT价格', name: 'price_usdt', type: 'number' }, { label: '启用', name: 'enabled', type: 'boolean' }, { label: '排序', name: 'sort', type: 'number' }],
  },
  numberOfOrders: {
    title: '笔数订单/次数', endpoint: '/energy/number-of-orders', description: '用户可用笔数、已用笔数和来源订单',
    columns: [{ title: '用户ID', dataIndex: 'user_id' }, { title: '机器人', dataIndex: 'bot_id' }, { title: '可用笔数', dataIndex: 'available_times' }, { title: '已用笔数', dataIndex: 'used_times' }, { title: '来源订单', dataIndex: 'source_order_no' }, { title: '到期时间', dataIndex: 'expire_at' }],
    fields: [{ label: '用户ID', name: 'user_id' }, { label: '机器人ID', name: 'bot_id' }, { label: '可用笔数', name: 'available_times', type: 'number' }, { label: '已用笔数', name: 'used_times', type: 'number' }, { label: '来源订单', name: 'source_order_no' }, { label: '到期时间', name: 'expire_at' }],
  },
  energyPenFlashEntries: {
    title: '能量闪租入口', endpoint: '/energy/pen-flash-entries', description: '闪租入口、地址和定价',
    columns: [{ title: '标题', dataIndex: 'title' }, { title: '机器人', dataIndex: 'bot_id' }, { title: '地址', dataIndex: 'address' }, { title: '能量', dataIndex: 'energy_amount' }, { title: 'TRX价格', dataIndex: 'price_trx' }, { title: '启用', dataIndex: 'enabled' }],
    fields: [{ label: '标题', name: 'title' }, { label: '机器人ID', name: 'bot_id' }, { label: '地址', name: 'address' }, { label: '能量', name: 'energy_amount', type: 'number' }, { label: 'TRX价格', name: 'price_trx', type: 'number' }, { label: '启用', name: 'enabled', type: 'boolean' }, { label: '排序', name: 'sort', type: 'number' }],
  },
  energyIntelligentPlans: {
    title: '智能托管套餐', endpoint: '/energy/intelligent-plans', description: '智能托管策略和能量区间',
    columns: [{ title: '名称', dataIndex: 'name' }, { title: '机器人', dataIndex: 'bot_id' }, { title: '最小能量', dataIndex: 'min_energy' }, { title: '最大能量', dataIndex: 'max_energy' }, { title: 'TRX价格', dataIndex: 'price_trx' }, { title: '策略', dataIndex: 'strategy' }, { title: '启用', dataIndex: 'enabled' }],
    fields: [{ label: '名称', name: 'name' }, { label: '机器人ID', name: 'bot_id' }, { label: '最小能量', name: 'min_energy', type: 'number' }, { label: '最大能量', name: 'max_energy', type: 'number' }, { label: 'TRX价格', name: 'price_trx', type: 'number' }, { label: '策略', name: 'strategy' }, { label: '启用', name: 'enabled', type: 'boolean' }, { label: '排序', name: 'sort', type: 'number' }],
  },
  energyRecords: {
    title: '能量租赁记录', endpoint: '/energy/records', description: '闪租/笔数/智能托管租赁执行记录',
    columns: [{ title: '订单号', dataIndex: 'order_no' }, { title: '用户ID', dataIndex: 'user_id' }, { title: '接收地址', dataIndex: 'receiver_address' }, { title: '模式', dataIndex: 'mode' }, { title: '能量', dataIndex: 'energy_amount' }, { title: '金额TRX', dataIndex: 'amount_trx' }, { title: '状态', dataIndex: 'status' }],
    fields: [{ label: '订单号', name: 'order_no' }, { label: '机器人ID', name: 'bot_id' }, { label: '用户ID', name: 'user_id' }, { label: '接收地址', name: 'receiver_address' }, { label: '模式', name: 'mode' }, { label: '能量', name: 'energy_amount', type: 'number' }, { label: '小时', name: 'duration_hours', type: 'number' }, { label: '笔数', name: 'number_of_times', type: 'number' }, { label: '金额TRX', name: 'amount_trx', type: 'number' }, { label: 'Hash', name: 'txid' }, { label: '状态', name: 'status' }],
    actions: [
      { name: 'success', label: '成功', path: 'success', promptField: 'txid', promptLabel: '请输入能量交易 Hash' },
      { name: 'fail', label: '失败', path: 'fail', danger: true, confirm: '确认标记失败？' },
    ],
  },
  exchangeRecords: {
    title: '兑换记录', endpoint: '/exchange/records', description: '兑换执行记录、汇率、手续费和Hash',
    columns: [{ title: '订单号', dataIndex: 'order_no' }, { title: '用户ID', dataIndex: 'user_id' }, { title: 'From', dataIndex: 'from_token' }, { title: 'To', dataIndex: 'to_token' }, { title: '原金额', dataIndex: 'from_amount' }, { title: '目标金额', dataIndex: 'to_amount' }, { title: '状态', dataIndex: 'status' }],
    fields: [{ label: '订单号', name: 'order_no' }, { label: '机器人ID', name: 'bot_id' }, { label: '用户ID', name: 'user_id' }, { label: 'From币种', name: 'from_token' }, { label: 'To币种', name: 'to_token' }, { label: '原金额', name: 'from_amount', type: 'number' }, { label: '目标金额', name: 'to_amount', type: 'number' }, { label: '汇率', name: 'rate', type: 'number' }, { label: '手续费', name: 'fee', type: 'number' }, { label: '状态', name: 'status' }, { label: '支付Hash', name: 'pay_txid' }, { label: '出款Hash', name: 'payout_txid' }],
    actions: [
      { name: 'markPaid', label: '已支付', path: 'mark-paid', promptField: 'txid', promptLabel: '请输入支付 Hash' },
      { name: 'markSent', label: '已出款', path: 'mark-sent', promptField: 'txid', promptLabel: '请输入出款 Hash' },
      { name: 'fail', label: '失败', path: 'fail', danger: true, confirm: '确认标记失败？' },
    ],
  },
  rechargeConfigs: {
    title: '充值配置', endpoint: '/finance/recharge-configs', description: '充值地址、币种、最小金额和确认数',
    columns: [{ title: '机器人', dataIndex: 'bot_id' }, { title: '币种', dataIndex: 'token_type' }, { title: '地址', dataIndex: 'address' }, { title: '最小金额', dataIndex: 'min_amount' }, { title: '确认数', dataIndex: 'confirmations' }, { title: '启用', dataIndex: 'enabled' }],
    fields: [{ label: '机器人ID', name: 'bot_id' }, { label: '币种', name: 'token_type' }, { label: '地址', name: 'address' }, { label: '最小金额', name: 'min_amount', type: 'number' }, { label: '确认数', name: 'confirmations', type: 'number' }, { label: '启用', name: 'enabled', type: 'boolean' }, { label: '备注', name: 'remark' }],
  },
};
