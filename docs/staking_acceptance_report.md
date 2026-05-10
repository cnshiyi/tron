# TRON 质押功能审查与验收报告

## 结论

本轮已对 TRON 原生质押、多签委托、自动回收、旧版数据兼容、前端入口、机器人 dry-run 能力做代码审查、修复和模拟测试。

当前可确认：

- 质押委托核心流程在模拟链客户端下可用。
- 多签签名数、Active Permission ID、委托、回收、到期回收均有单元测试覆盖。
- 前端类型检查已通过。
- 后端项目已使用 Shop 项目的机器人 token 写入本地 Bot 配置并启动。
- 为安全起见，真实 Telegram 发送和真实链上广播仍保持关闭；本轮只做 dry-run 和本地启动，不对外发送消息、不广播链上交易。

## 已修复问题

### 1. 质押委托成功状态不利于自动回收

原逻辑在真实广播成功后仍把 `StakingOrder.status` 保持为 `delegating`，而自动回收只扫描 `success` 状态，导致已委托订单无法被定时回收。

修复后：

- `broadcast=True` 且签名/广播成功：`EnergyOrder.status = success`，`StakingOrder.status = success`。
- 自动写入 `expire_at`，默认按套餐 `duration_hours` 计算；无套餐时按 1 小时。
- `broadcast=False` 演练仍保持 `pending`，不会消耗库存。

### 2. 回收接口缺少状态保护

原逻辑允许非成功状态订单进入回收流程。

修复后：

- 只有 `success` 或 `reclaiming` 状态可回收。
- `pending/delegating/failed/reclaimed` 等状态会拒绝回收。

### 3. 前端类型检查失败

修复了两个前端类型问题：

- `Dashboard.vue` 中统计卡片数组未显式声明 tuple 类型。
- `ResourcePage.vue` 中表格固定列 `fixed` 类型过宽。

## 验证结果

### 后端单元测试

```bash
.venv/bin/python manage.py test -v 1
```

结果：6 个测试全部通过。

覆盖范围：

- 多签委托会应用 `permission_id`。
- 多签委托会按 `required_signature_count` 签名。
- 能量订单可生成质押委托订单。
- dry-run 不消耗库存、不改变订单为成功。
- 到期自动回收只回收成功且到期的订单。
- 非成功委托订单禁止回收。

### 前端类型检查

```bash
pnpm --dir frontend --filter @vben/web-antd typecheck
```

结果：通过。

注意：当前 Node 是 `v25.9.0`，项目声明推荐 `^20.19.0 || ^22.18.0 || ^24.0.0`，pnpm 有引擎警告，但不影响本次 typecheck 通过。

### 全接口模拟测试

模拟脚本创建了质押账户、能量订单、机器人、群组、推广、用户、余额、地址、监听、兑换、会员、旧版兼容数据，并验证 29 个接口返回 200。

结果：`SIMULATION_OK 29 endpoints`。

覆盖接口包括：

- `/api/dashboard/`
- `/api/reports/overview/`
- `/api/bots/`
- `/api/telegram/webhook/<bot_id>/`
- `/api/users/`
- `/api/addresses/`
- `/api/exchange/*`
- `/api/energy/*`
- `/api/staking/*`
- `/api/membership/*`
- `/api/finance/*`
- `/api/legacy/game-records/`
- `/api/game/tgConfig/list`

## 启动结果

### 后端

- 地址：`http://127.0.0.1:18001`
- PID：见 `/tmp/tron-backend.pid`
- 日志：`/tmp/tron-backend.log`
- 健康验证：`GET /api/dashboard/` 返回 200。

### 前端

- 地址：`http://127.0.0.1:15666`
- PID：见 `/tmp/tron-frontend.pid`
- 日志：`/tmp/tron-frontend.log`
- 健康验证：`HEAD /` 返回 200。

### Shop 机器人 token

已从 `/Users/aaaa/Desktop/shop/.env` 读取 `BOT_TOKEN`，并写入 TRON 本地数据库 `bots.Bot`。

安全说明：报告中只显示掩码，不输出完整 token；本轮未启用真实发送。

## 仍需生产前确认

以下项目无法通过本地模拟证明“生产 100% 可用”，需要生产配置或测试网资源确认：

1. 真实 TRON 节点/Trongrid 网络可达性。
2. 质押账户真实权限、权重、多签私钥是否匹配链上 Active Permission。
3. 真实能量委托和回收是否被链上确认。
4. Telegram Webhook 公网域名、证书、回调可达性。
5. 私钥字段当前仍由业务字段承载，生产前建议接入专用密钥管理或加密方案。
