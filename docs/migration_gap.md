# TRON 旧系统完整迁移清单

目标：旧 Vue2/JEECG 前端和 Java 后端功能，逐步 1:1 搬到当前 Django + DRF + Vben Admin 项目。

当前状态：已完成可运行基础版，含 Vben 登录、TRON 菜单、主要业务基础 CRUD、Telegram Webhook/SOHU/TRON 服务骨架。还不是完整复刻。

## 已确认新增需求

- 支持同时添加多个 Telegram 机器人：已实现 `/api/bots/bulk-create/`，前端机器人管理页新增“批量添加机器人”。

## 旧前端页面盘点

- TgAdvanceRecordList.vue: 基础覆盖：预支记录 CRUD/API 已迁入。
- TgConfigList.vue: 部分覆盖：系统配置 Settings.vue.
- TgEnergyAgentRecordList.vue: 基础覆盖：能量代理记录 CRUD/API 已迁入。
- TgEnergyHourlyList.vue: 合并覆盖：能量套餐/能量订单.
- TgEnergyHourlyTimeList.vue: 待迁移：需要新增 Vben 专用页面/后端模型接口.
- TgEnergyHourlyTimePiceList.vue: 待迁移：需要新增 Vben 专用页面/后端模型接口.
- TgEnergyIntelligentAddressList.vue: 基础覆盖：能量地址配置 CRUD/API 已迁入。
- TgEnergyIntelligentList.vue: 待迁移：需要新增 Vben 专用页面/后端模型接口.
- TgEnergyPenAddressList.vue: 基础覆盖：能量地址配置 CRUD/API 已迁入。
- TgEnergyPenFlashEntList.vue: 待迁移：需要新增 Vben 专用页面/后端模型接口.
- TgEnergyPenList.vue: 待迁移：需要新增 Vben 专用页面/后端模型接口.
- TgEnergyRecordList.vue: 待迁移：需要新增 Vben 专用页面/后端模型接口.
- TgExchangeBlackList.vue: 覆盖基础 CRUD：兑换黑名单.
- TgExchangeList.vue: 部分覆盖：兑换订单.
- TgExchangeRecordList.vue: 待迁移：需要新增 Vben 专用页面/后端模型接口.
- TgGroupList.vue: 部分覆盖：群组管理 ResourcePage.
- TgListerAddressList.vue: 基础覆盖：监听地址 CRUD/API 已迁入。
- TgMemberActivityList.vue: 基础覆盖：会员活动 CRUD/API 已迁入。
- TgMemberGoodsList.vue: 覆盖基础 CRUD：会员商品.
- TgMemberOrderList.vue: 覆盖基础 CRUD：会员订单.
- TgMemberRechargeList.vue: 基础覆盖：会员充值 CRUD/API 已迁入。
- TgNumberOfOrdersList.vue: 待迁移：需要新增 Vben 专用页面/后端模型接口.
- TgPromotionList.vue: 部分覆盖：推广文案 ResourcePage.
- TgRechargeConfigList.vue: 待迁移：需要新增 Vben 专用页面/后端模型接口.
- TgRunningWaterList.vue: 覆盖基础 CRUD：资金流水.
- TgUserList.vue: 基础覆盖：用户管理 CRUD/API 已迁入。
- TgUserTopList.vue: 基础覆盖：用户排行 CRUD/API 已迁入。

## 后端待补齐方向

- 用户体系：TgUser、用户排行、用户拉黑/置顶、用户机器人归属、会员权益联动。
- 能量业务细分：小时套餐、小时价格、笔数套餐、笔数地址、智能托管、智能托管地址、闪租入口、代理订单、佣金、预支记录。
- 兑换业务细分：兑换配置、兑换订单、兑换记录、黑名单、TRX/USDT 链上监听、自动出款、利润统计。
- 会员业务细分：会员商品、会员订单、会员充值、会员活动、会员佣金。
- 财务业务：余额流水、提现审核、链上打款、充值配置、监听地址。
- 机器人业务：多机器人配置、群组绑定、自动回复、按钮、群发/收益播报、Telegram webhook 按机器人分发。
- 统计报表：用户、订单、收益、佣金、兑换、能量租赁多维统计。

## 执行顺序建议

1. 机器人/群组/推广完整化
2. 用户管理与余额体系
3. 能量套餐与能量订单全模型
4. 兑换监听与兑换记录
5. 会员充值/活动/佣金
6. 提现/充值配置/地址监听
7. 统计报表与生产权限