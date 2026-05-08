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
- TgEnergyHourlyTimeList.vue: 基础覆盖：能量时长配置 CRUD/API 已迁入。
- TgEnergyHourlyTimePiceList.vue: 基础覆盖：能量时长价格 CRUD/API 已迁入。
- TgEnergyIntelligentAddressList.vue: 基础覆盖：能量地址配置 CRUD/API 已迁入。
- TgEnergyIntelligentList.vue: 基础覆盖：智能托管套餐 CRUD/API 已迁入。
- TgEnergyPenAddressList.vue: 基础覆盖：能量地址配置 CRUD/API 已迁入。
- TgEnergyPenFlashEntList.vue: 基础覆盖：能量闪租入口 CRUD/API 已迁入。
- TgEnergyPenList.vue: 基础覆盖：能量笔数套餐 CRUD/API 已迁入。
- TgEnergyRecordList.vue: 基础覆盖：能量租赁记录 CRUD/API 已迁入。
- TgExchangeBlackList.vue: 覆盖基础 CRUD：兑换黑名单.
- TgExchangeList.vue: 部分覆盖：兑换订单.
- TgExchangeRecordList.vue: 基础覆盖：兑换记录 CRUD/API 已迁入。
- TgGroupList.vue: 部分覆盖：群组管理 ResourcePage.
- TgListerAddressList.vue: 基础覆盖：监听地址 CRUD/API 已迁入。
- TgMemberActivityList.vue: 基础覆盖：会员活动 CRUD/API 已迁入。
- TgMemberGoodsList.vue: 覆盖基础 CRUD：会员商品.
- TgMemberOrderList.vue: 覆盖基础 CRUD：会员订单.
- TgMemberRechargeList.vue: 基础覆盖：会员充值 CRUD/API 已迁入。
- TgNumberOfOrdersList.vue: 基础覆盖：笔数订单/次数 CRUD/API 已迁入。
- TgPromotionList.vue: 部分覆盖：推广文案 ResourcePage.
- TgRechargeConfigList.vue: 基础覆盖：充值配置 CRUD/API 已迁入。
- TgRunningWaterList.vue: 覆盖基础 CRUD：资金流水.
- TgUserList.vue: 基础覆盖：用户管理 CRUD/API 已迁入。
- TgUserTopList.vue: 基础覆盖：用户排行 CRUD/API 已迁入。

## 后端待补齐方向

- 用户体系：TgUser、用户排行、用户机器人归属已基础覆盖；用户拉黑/取消拉黑、置顶/取消置顶后台操作已迁入；会员权益联动待深化。
- 能量业务细分：小时套餐、小时价格、笔数套餐、笔数地址、智能托管、智能托管地址、闪租入口、代理订单、佣金、预支记录已基础覆盖；能量订单支付/委托中/成功/失败、预支审核操作已迁入。
- 兑换业务细分：兑换配置、兑换订单、兑换记录、黑名单已基础覆盖；兑换订单/记录已支持已支付、已出款、失败、取消等后台流转；TRX/USDT 链上监听、自动出款、利润统计待深化。
- 会员业务细分：会员商品、会员订单、会员充值、会员活动、会员佣金已覆盖；会员订单已支持已支付/开通权益/取消，会员充值可确认到账并写余额流水，会员佣金可按邀请人结算到余额。
- 财务业务：余额流水、提现审核、充值配置、监听地址已基础覆盖；余额手工调账、提现通过/拒绝/已打款后台操作已迁入；真实链上打款待接入私钥/多签策略。
- 机器人业务：多机器人配置、群组绑定、自动回复、按钮、Webhook 用户/群组识别、/start 邀请关系、群发演练、群发记录已覆盖；真实群发/收益播报需开启 TELEGRAM_SEND_ENABLED 并接入生产域名。
- 统计报表：用户、订单、收益、佣金、兑换、能量租赁多维统计已迁入控制台和 `/api/reports/overview/`；更复杂图表、按机器人/日期筛选待深化。

## 执行顺序建议

1. 机器人/群组/推广完整化
2. 用户管理与余额体系
3. 能量套餐与能量订单全模型
4. 兑换监听与兑换记录
5. 会员充值/活动/佣金
6. 提现/充值配置/地址监听
7. 统计报表与生产权限