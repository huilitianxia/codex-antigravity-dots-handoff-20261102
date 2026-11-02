# 4A 批量改价与折扣价操作方案

## 结论

当前 Codex 插件列表中没有可直接登录 Amazon Seller Central 并一键改价的官方 Amazon 插件。最稳妥的方式是使用 Seller Central 官方批量模板；若要持续自动跟价，则使用 Amazon 自带的 Automate Pricing。若需要完全自动化，可另行开发 Selling Partner API 集成或选用 Selling Partner Appstore 的第三方工具。

## 一次性批量改价

1. 在美国站 Seller Central 下载当前官方 `Price & Quantity` 模板；如需批量维护 List Price，则下载对应品类的 Advanced/Custom inventory template，并包含 Offer 属性。
2. 用 2026 总表映射：
   - `SKU` → Amazon 模板的 seller SKU 字段。
   - `折后销售价 2026` → 当前销售价格字段。
   - `标价` → 仅在有真实、可验证的 MSRP/外部零售价或历史 Amazon 成交依据时，映射到 List Price。
   - 可选：最低允许价、最高允许价、Sale 起止日期等，以当次下载模板的真实列名为准。
3. 采用 `PartialUpdate`，只更新报价相关字段，避免覆盖标题、图片、变体等目录信息。
4. 先上传 3–5 个 SKU；下载并检查 Processing Report。确认无错误且前台显示正确后再批量上传。

不要直接根据旧模板猜列名。Amazon 会调整模板和校验规则，必须以当前店铺、当前站点下载的文件为准。

## 三种“原价＋优惠价”方式

### A. List Price + 当前售价

适合有真实 MSRP、近期外部零售价或 Amazon 历史成交价的产品。List Price 被验证后，当前售价低于它时才可能出现划线对比；提交成功不等于一定显示。

2026 年 4 月 23 日起，Amazon 要求卖家提交的 List Price 至少满足其一：近期在其他零售商以该价格提供，或客户曾在 Amazon 以该 List Price 作为 Featured Offer 成交。因此不应人为抬高“原价”制造折扣感。

### B. Price Discounts

更适合新品推广或阶段性促销。进入 Seller Central 的 Price Discounts dashboard，创建折扣、设置开始/结束时间、折扣类型、受众与商品。官方说明该活动最长可运行 30 天、可限制数量；只有通过资格校验且具有有效参考价的产品，才会在搜索和详情页显示划线价。

### C. Coupons

进入 `Advertising → Coupons`，按 ASIN 添加固定金额或百分比优惠。Coupon 的视觉信号明确，但会产生兑换费用；还要避免与 Price Discount 或其他促销叠加造成过度折扣。

## 推荐给 4A 的组合

- 常态价格：先把真正有竞争力且可盈利的价格设为当前销售价，不靠虚高 List Price。
- 有真实零售证据的 SKU：维护合规 List Price，用于稳定参考价。
- 主推款：以 7–14 天 Price Discount 做测试，观察转化、广告效率和利润；结束后复盘，不要长期连续处于折扣状态。
- 需要搜索页醒目标签的少数 SKU：再使用 Coupon，但先计算兑换费并排除折扣叠加。
- 竞争激烈且已有报价的 SKU：使用 `Pricing → Automate Pricing`，为每个 SKU 设最低价和可选最高价，防止自动跟价跌穿利润底线。

## 上线前检查

- 修正 `4A 6031x4`、`4A 301Mx24`、`4A 303M-PNx12` 的反向价格。
- 为 68 个只有标价的 SKU 决定是否填写目标销售价；2 个双空 SKU 暂不上传价格。
- 每个 SKU 计算最低可接受价：到岸成本 + FBA/配送费 + 佣金 + 广告预算 + 目标利润。
- 保存每次上传的原文件、上传文件、处理报告与生效时间，便于回滚和追踪。

## 官方参考

- Automate Pricing: https://sell.amazon.com/tools/automate-pricing
- Promotions, Coupons and Price Discounts: https://sell.amazon.com/blog/seller-promotions
- 2026 Reference Pricing Update: https://sellercentral.amazon.com/seller-forums/discussions/t/f48a1fe5-aa8e-4806-b687-2d9aeec5c351

