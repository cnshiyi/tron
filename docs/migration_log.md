# 迁移日志

## JJC-20260510-001 完整迁移TRX质押版本功能

### 输入来源

- 压缩包：`/Users/aaaa/Downloads/TRX质押版本.rar`
- 解包目录：`.migration/source_trx_staking/TRX质押版本/`
- 旧 SQL：`.migration/source_trx_staking/TRX质押版本/shiyinengliang.sql`
- 旧前端：`.migration/source_trx_staking/TRX质押版本/vue-jeecg-duihuan/`

### 迁移步骤

1. 定位桌面目标项目：`/Users/aaaa/Desktop/tron`。
2. 解包 `TRX质押版本.rar`，确认旧项目为 Jeecg Vue2 + SQL dump。
3. 盘点旧版 `src/views/game/Tg*.vue`，确认 27 个 TRX/能量/会员/兑换/用户页面。
4. 盘点旧版 `tg_` 表，确认业务数据集中在 27 张旧表。
5. 新增 Django `legacy` 应用和 `LegacyGameRecord` 模型。
6. 新增旧版 `/api/game/<resource>/<action>` 兼容接口。
7. 新增 `import_trx_legacy_sql` 导入命令。
8. 新增前端 `/tron/legacy-game` 旧版数据查看页面。
9. 执行 Django 迁移并导入旧 SQL 业务数据。
10. 补充迁移说明文档和 README 入口说明。

### 导入结果

实际导入旧版业务记录 420 条：

| 资源 | 数量 |
| --- | ---: |
| tgConfig | 1 |
| tgEnergyAgentRecord | 8 |
| tgEnergyHourly | 1 |
| tgEnergyHourlyTime | 1 |
| tgEnergyHourlyTimePice | 42 |
| tgEnergyIntelligent | 1 |
| tgEnergyIntelligentAddress | 1 |
| tgEnergyPen | 7 |
| tgEnergyPenAddress | 3 |
| tgEnergyPenFlashEnt | 1 |
| tgEnergyRecord | 143 |
| tgExchangeBlack | 3 |
| tgExchangeRecord | 56 |
| tgGroup | 1 |
| tgListerAddress | 6 |
| tgMemberGoods | 3 |
| tgMemberOrder | 4 |
| tgMemberRecharge | 49 |
| tgNumberOfOrders | 3 |
| tgPromotion | 64 |
| tgRechargeConfig | 18 |
| tgUser | 4 |

### 验证命令

```bash
.venv/bin/python manage.py check
.venv/bin/python manage.py import_trx_legacy_sql .migration/source_trx_staking/TRX质押版本/shiyinengliang.sql --dry-run
.venv/bin/python manage.py migrate legacy
.venv/bin/python manage.py import_trx_legacy_sql .migration/source_trx_staking/TRX质押版本/shiyinengliang.sql --clear
```

### 注意事项

- `.migration/` 是本地解包工作目录，不纳入 Git。
- `db.sqlite3` 是本地数据库，不纳入 Git。
- 旧 SQL 中具有私钥语义的字段只作为旧版 JSON 数据保留，未自动写入新版出款或质押模型。
