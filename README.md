# TRON Energy Bot Platform

前后端分离版本，后端使用 Django + DRF，前端基于 vue-vben-admin 二次开发。

## 已搭建的业务模块

- bots：Telegram 机器人、Webhook、自动回复、推广按钮、群组播报配置
- wallet：TRON 地址池、TRC20/USDT 交易查询服务骨架
- exchange：USDT/TRX 兑换配置、订单、黑名单
- energy：能量闪租、时长/笔数/智能托管套餐、订单、sohu 能量平台回调
- membership：会员商品、会员订单
- finance：余额、流水、提现审批
- accounts：后台仪表盘 API

## 本地启动

```bash
uv sync
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver 0.0.0.0:8000
```

前端在 `frontend/`，来自 `https://github.com/vbenjs/vue-vben-admin`，后续在此目录内二次开发对接 `/api/`。

## API

- `/admin/` Django 管理后台
- `/api/dashboard/` 仪表盘统计
- `/api/bots/` 机器人管理
- `/api/telegram/webhook/<bot_id>/` Telegram Webhook
- `/api/wallet/probe/<address>/` TRON 账户/交易探测
- `/api/exchange/*` 兑换业务
- `/api/energy/*` 能量业务
- `/api/membership/*` 会员业务
- `/api/finance/*` 财务业务
