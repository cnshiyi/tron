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
- legacy：兼容 `TRX质押版本.rar` 的旧版 Jeecg `/game/tg*` 接口、SQL 导入和原始数据查看

## 本地启动

默认开发端口已改为避免冲突：

- 后端：http://127.0.0.1:18001
- 前端：http://127.0.0.1:15666

后端一键启动：

```bash
python3 start_backend.py
```

如果后端已经在运行，脚本不会直接退出，会持续健康检查并打印状态。想让脚本重启后端并接管 Django 实时请求日志：

```bash
python3 start_backend.py --restart
```

macOS 也可以直接双击根目录的 `start_backend.command`，它会使用 `--restart` 方式启动，窗口会持续打印 Django 日志。

手动启动：

```bash
uv sync
uv run python manage.py migrate
uv run python manage.py runserver 127.0.0.1:18001
```

默认后台登录：

- 账号：admin
- 密码：123456
- Google 验证码：123456

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
- `/api/game/<resource>/<action>` 旧版 TRX 质押 Jeecg 接口兼容层
- `/api/legacy/game-records/` 旧版 TRX 质押原始数据管理

## TRX质押版本迁移

已支持从下载目录 `TRX质押版本.rar` 解包出的旧 SQL 导入 27 个 `tg_` 业务表，并在前端提供 `/tron/legacy-game` 查看入口。

```bash
.venv/bin/python manage.py import_trx_legacy_sql .migration/source_trx_staking/TRX质押版本/shiyinengliang.sql --dry-run
.venv/bin/python manage.py import_trx_legacy_sql .migration/source_trx_staking/TRX质押版本/shiyinengliang.sql --clear
```

迁移说明见 `docs/trx_staking_migration.md`，执行日志见 `docs/migration_log.md`。
