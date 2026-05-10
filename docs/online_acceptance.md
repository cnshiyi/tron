# 线上实测补充说明

## 当前补齐内容

本次补齐了线上实测所需的配置项、就绪检查命令和操作说明。

- `.env.example` 已补齐 `PUBLIC_BASE_URL`、`TELEGRAM_DELIVERY_MODE`、`TRON_NETWORK`、`TELEGRAM_SEND_ENABLED`、`SOHU_SEND_ENABLED`、`WITHDRAWAL_PAYOUT_ENABLED` 等开关。
- 新增命令 `check_online_readiness`，用于检查公网地址或轮询模式、Trongrid Key、机器人 token、质押账户等是否就绪。
- 新增 Telegram 轮询命令 `run_telegram_polling`，无需域名即可收消息。
- 本地 `.env` 已生成安全默认值，真实发送和链上广播仍默认关闭。

## 就绪检查

```bash
.venv/bin/python manage.py check_online_readiness
```

严格模式：

```bash
.venv/bin/python manage.py check_online_readiness --strict
```

## 三档实测方式

### 1. 安全联通测试

目标：验证后端、前端、机器人配置，不发送真实群消息、不广播链上交易。

要求：

```env
TELEGRAM_SEND_ENABLED=0
SOHU_SEND_ENABLED=0
WITHDRAWAL_PAYOUT_ENABLED=0
```

### 2. 无域名 Telegram 轮询实测

目标：不用公网域名，通过 Telegram `getUpdates` 拉取消息。

要求：

```env
TELEGRAM_DELIVERY_MODE=polling
TELEGRAM_SEND_ENABLED=0
```

只拉取一次验证：

```bash
.venv/bin/python manage.py run_telegram_polling --once --dry-run
```

持续轮询：

```bash
.venv/bin/python manage.py run_telegram_polling --dry-run
```

如果要真实回复消息，需要明确开启：

```env
TELEGRAM_SEND_ENABLED=1
```

### 3. Telegram Webhook 实测

目标：验证公网回调和 Telegram API。

要求：

```env
TELEGRAM_DELIVERY_MODE=webhook
PUBLIC_BASE_URL=https://你的公网域名
TELEGRAM_SEND_ENABLED=1
```

执行前确认：公网域名必须能访问本项目后端 `/api/telegram/webhook/<bot_id>/`。

### 4. TRON 测试网/主网小额实测

目标：验证真实多签、委托、回收。

要求：

```env
TRON_NETWORK=nile 或 mainnet
TRONGRID_API_KEY=你的key
```

主网前建议先用测试网跑通；主网只用小额 TRX 和指定测试地址。

## 不能自动补齐的内容

以下内容必须由线上环境或皇上授权后才能填写：

- Webhook 模式需要公网域名 `PUBLIC_BASE_URL`；轮询模式不需要
- Trongrid API Key
- 真实质押账户私钥/多签私钥
- 真实接收测试地址
- 是否允许 Telegram 真实发送
- 是否允许 TRON 链上广播

## 安全默认值

本项目默认保持：

- 不真实发送 Telegram 消息。
- 不调用三方能量真实下单。
- 不真实出款。
- 质押接口默认前端演练参数 `broadcast=false`。
