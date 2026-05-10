# TRX质押版本功能迁移说明

## 目标

将下载目录 `TRX质押版本.rar` 中旧 Jeecg/Vue2 项目的 TRX 质押业务能力迁入当前 Django + DRF + Vben 项目。

## 旧版功能范围

旧版业务集中在 `shiyinengliang.sql` 的 27 张 `tg_` 表和前端 `src/views/game/Tg*.vue` 页面：

- 系统配置：`tg_config`
- 用户与排行：`tg_user`、`tg_user_top`
- 群组与推广：`tg_group`、`tg_promotion`
- 充值与监听：`tg_recharge_config`、`tg_lister_address`
- 资金流水：`tg_running_water`
- 兑换：`tg_exchange`、`tg_exchange_black`、`tg_exchange_record`
- 能量：`tg_energy_record`、`tg_energy_agent_record`、`tg_energy_hourly*`、`tg_energy_pen*`、`tg_energy_intelligent*`、`tg_number_of_orders`
- 会员：`tg_member_goods`、`tg_member_order`、`tg_member_recharge`、`tg_member_activity`
- 预支：`tg_advance_record`

## 当前迁移实现

### 1. 旧版接口兼容

新增 `legacy` 应用，提供旧 Jeecg 页面依赖的兼容接口：

```text
/api/game/<resource>/list
/api/game/<resource>/add
/api/game/<resource>/edit
/api/game/<resource>/queryById
/api/game/<resource>/delete
/api/game/<resource>/deleteBatch
/api/game/<resource>/exportXls
```

`resource` 支持旧版所有 27 个资源名，例如 `tgConfig`、`tgEnergyRecord`、`tgExchangeRecord`、`tgUser`。

### 2. 数据承接

旧版表字段大量与当前新版模型不完全 1:1，因此用 `LegacyGameRecord` 保存完整原始字段：

- `resource`：旧版接口资源名
- `table_name`：旧 SQL 表名
- `legacy_id`：旧主键
- `data`：旧表完整字段 JSON

这样不会丢失旧版字段、状态枚举、金额精度、交易 hash、按钮排序、消息 ID 等信息。

### 3. 导入命令

```bash
.venv/bin/python manage.py import_trx_legacy_sql \
  .migration/source_trx_staking/TRX质押版本/shiyinengliang.sql \
  --clear
```

可先 dry-run：

```bash
.venv/bin/python manage.py import_trx_legacy_sql \
  .migration/source_trx_staking/TRX质押版本/shiyinengliang.sql \
  --dry-run
```

### 4. 前端入口

新增 Vben 页面：

```text
/tron/legacy-game
```

菜单标题：`旧版TRX质押数据`。该页面可以按 27 个旧版资源查看导入后的原始字段。

## 与新版模型的关系

当前项目已经有新版领域模型：

- 原生质押/多签：`StakingAccount`、`StakingOrder`、`StakingTransaction`
- 能量订单/套餐：`EnergyOrder`、`EnergyPlan`、`EnergyRecord` 等
- 兑换：`ExchangeConfig`、`ExchangeOrder`、`ExchangeRecord`
- 用户/余额/流水：`TgUser`、`Balance`、`RunningWater`
- 会员：`MemberGoods`、`MemberOrder`、`MemberRecharge`

旧版完整字段先进入 `LegacyGameRecord`，新版业务可按需要从 `data` 中做二次归档或重放；涉及私钥、出款、链上广播的字段不做明文自动迁入，避免生产安全风险。

## 已知安全说明

旧 SQL 含兑换出款私钥、质押地址私钥等字段语义。迁移命令保留原字段到兼容 JSON 中，不会主动广播链上交易，也不会将私钥注入新版出款/质押模型。上线前应执行：

1. 用正式密钥管理方案加密私钥字段。
2. 关闭开发登录默认账号密码。
3. 关闭 `DEBUG` 和 `CORS_ALLOW_ALL_ORIGINS`。
4. 用 `StakingAccount.sync` 重新同步链上质押状态。
