# 4A 亚马逊全店运营与 Listing 变体交接文档 (Handoff 2026-11-06)

**交接时间**：2026-11-06 16:30 (北京时间)  
**责任主体**：Antigravity Coding Assistant  
**GitHub 归档仓库**：`https://github.com/huilitianxia/codex-antigravity-dots-handoff-20261102`  
**会话 ID**：`a9c9debb-a9a7-4aef-9dfe-40a94ab2980d`

---

## 一、 本会话核心执行事项与最新状态大盘

| 模块 | 核心任务 | 当前状态 | 关键数据 / 参数 / 批次 |
| :--- | :--- | :--- | :--- |
| **301 家族变体** | 9大变体合并至旗舰父体 `B01LVWFZVZ` | **批次 23 已处理** (后台显示 2/10 成功，需查明细) | 批次号: `287106020763` |
| **30315 广告** | 精准组与自动组提价促曝光 | **已生效运行** | Exact: $2.20~$2.80 (+50% Top), Auto: $0.75 (+30% Top) |
| **30315 定价** | 调价至 $19.99 + 5% Coupon | **已在前台与后台生效** | 优惠券：`节省 5% 4A Office Sticky Notes Liquidation` |
| **30315-Z** | 独立款广告与变体管理 | **严格保持暂停 (Paused)** | ASIN: `B07RP82CVJ`，暂不加广告预算 |
| **2028-N (2x2)** | FBM 改包邮 $9.99 与广告准备 | **已完成策略推演，待后台配置** | SKU: `4A 2028-N-B07DJ-FBM`，库存 1,473 |
| **满胶 (Full Glue)** | 6大爆款出单监控与阶梯价规划 | **正在密集出单，已拟定阶梯价** | 涵盖 304, 305, 302 及大包装，建议 3%/5%/8% 阶梯 |
| **608-NL-210** | 6x8 便签旧 VC 页面出单归因 | **原因查明** | 历史复购流量 + 自然排名沉淀 + Prime 现货极速达 |

---

## 二、 301 家族 9 个变体合并深度排查与交接

### 1. 变体合并架构
* **旗舰页面（父体载体）**：ASIN `B01LVWFZVZ`，SKU `4A301x12-Y-B01LVW-FBM`
* **父体 SKU**：`PARENT-4A-301-MINI-PADS`
* **变体主题 Theme**：`COLOR/SIZE` 双维度
* **纳入合并的 9 大子体**：
  1. `Canary Yellow` x `12 Pads (1,200 Sheets)`: SKU `4A301x12-Y-B01LVW-FBM`, ASIN `B01LVWFZVZ`
  2. `Canary Yellow` x `24 Pads (2,400 Sheets)`: SKU `4A 301x24`, ASIN `B01LVXOCU2` (已纠正旧重定向 ASIN B01N5FAJAR)
  3. `Canary Yellow` x `48 Pads (4,800 Sheets)`: SKU `4A 301x24-Y`, ASIN `B01N9HHKRM`
  4. `Neon Assorted` x `12 Pads (1,200 Sheets)`: SKU `4A 301x12-N`, ASIN `B01LVTWP7Q`
  5. `Neon Assorted` x `24 Pads (2,400 Sheets)`: SKU `AAAA 4A 301x12-N`, ASIN `B07FK8LN8D`
  6. `Neon Assorted` x `48 Pads (4,800 Sheets)`: SKU `4A GM301x24*2`, ASIN `B07FKD3DBJ`
  7. `8 Colors Assorted` x `18 Pads (1,800 Sheets)`: SKU `4A 354818`, ASIN `B07DJKDB63`
  8. `8 Colors Assorted` x `36 Pads (3,600 Sheets)`: SKU `4A 354818*2`, ASIN `B07FK6867S`
  9. `8 Colors Assorted` x `72 Pads (7,200 Sheets)`: SKU `4A GM354818*4`, ASIN `B07MGH2KWS`

### 2. 昨晚（批次 22，Feed 286845020762）失败归因
1. **父体未成功创建**：父体 `PARENT-4A-301-MINI-PADS` 误用了 `PartialUpdate`，亚马逊拒绝部分更新不存在的全新 SKU（Warning 13013）。
2. **要点政策冲突**：子体携带了 `Item Highlight`，违反亚马逊新规（标题 > 75 字符禁止附带 Highlight，触发 Error 100476）。
3. **配送模板误传**：FBA SKU 误传了自配送运费模板，触发 Error 12998。

### 3. 今日（批次 23，Feed 287106020763）处理与待办
* **模板文件**：`23-flagship-9-variations-clean.xlsm`
  * 存放路径：
    - `D:\4A\00_当前工作区_202611\23-flagship-9-variations-clean.xlsm`
    - `E:\Desktop\23-flagship-9-variations-clean.xlsm`
    - `E:\OpenAI-Codex\天皇のcodex\23-flagship-9-variations-clean.xlsm`
  * 架构改进：父体采用 `Create or Replace (Full Update)`，子体全部采用纯净 `Edit (Partial Update)`，去除全部冗余字段与价格配送模板。
* **后台状态**：Feed ID `287106020763` 显示 `2 / 10`。
* **新会话首要动作**：
  - 在卖家后台“批量上传商品”状态页点击批次 `287106020763` 右侧的“下载处理一览（Processing Summary）”。
  - 查看具体哪 8 个子体在挂载时返回了报错（通常是品牌归属、分类一致性或特定必填字段提示），完成针对性字段微调后再次上传。

---

## 三、 30315 广告与价格联动落地

1. **价格与优惠券现状**：
   * 售价已成功调整为 **$19.99**（库存管理后台已保存生效）。
   * 优惠券已生效：**5% 优惠券**（前台展示立减 5%，折后约 $18.99，极具清仓竞争力）。
2. **广告竞价大幅提升**：
   * **精准广告组** (`SP_REACTIVATE_B4_30315_EXACT_20261102`)：
     - 主力大词出价已提升至 **$2.20 ~ $2.80**，同时设置了 **+50% 首页首位加价（Top-of-Search）**。
   * **自动广告组** (`SP_DISCOVERY_30315_AUTO_CLOSE_20261104`)：
     - 紧密匹配（Close Match）出价提升至 **$0.75**，加价比例 **+30%**。
3. **防坑提示**：
   * `4A GM30315-Z` (`B07RP82CVJ`) 表现欠佳且未与本体合并，**严禁开启广告**，维持 Paused 状态。

---

## 四、 2028-N (2x2 小号便签, B07DJXC4PJ) 接管策略

1. **现状**：
   * SKU：`4A 2028-N-B07DJ-FBM`，ASIN：`B07DJXC4PJ`
   * 当前价格：$4.99 + $4.99 运费（实付 $9.98）。
   * 库存格局：亚马逊自营（AMZ）卖 $6.49 仅剩 4 件；4A FBA 卖 $8.99 仅剩 3 件；4A FBM 库存高达 **1,473 件**。
2. **执行方案**：
   * 将配送模板变更为 **包邮模板（Free Shipping Template）**。
   * 商品售价调整为 **$9.99 包邮**。
   * 逻辑：对比 FBA 的 $8.99 仅高出 $1.00。在自营和 FBA 合计 7 件现货售罄后，$9.99 包邮的 1,473 件大库存将无缝取得购物车（Buy Box）。
   * 广告配置：为其新建 SP 广告活动，出价采用中高出价（高于建议出价中位数），确保前台曝光。

---

## 五、 608-NL-210 (6x8 英寸) 旧 VC 页面出单原因

* **现象**：广告绑定了新页面图二（`B07B8RBCKT`），但旧 VC 页面图一（`B07HDVVZ1B`）FBA 库存莫名出了两单。
* **排查结论**：
  1. **买家“再次购买（Buy Again）”黏性**：6x8 尺寸多为学校或办公用户，常直接在历史订单中点击复购，流量直接回流旧 ASIN。
  2. **自然搜索权重长期留存**：旧页面在“6x8 lined sticky notes rainbow”等特定长尾词上享有数年沉淀的自然排名。
  3. **Prime 现货极速达**：旧页面 FBA 当时有现货，转化率极高。

---

## 六、 满胶 (Full Adhesive) 系列出单监控与 B2B 阶梯价方案

### 1. 今日爆发订单明细
* `4A 304 Full Glue` (`B00SMEFFRE`, 4 1/3 x 3 in): $9.49
* `4A 305-Full Adhesive` (`B0FBG138ND`, 3 x 5 in): $10.99
* `AAAA 4A 304-Full Glue` (`B07FK975YB`, 3 x 4 in 10本装): $12.34 (**企业买家采购**)
* `4A 302-Full Adhesive-400` (`B0F2TKL2P5`, 3 x 2 in 400张): $17.09
* `AAAA 4A 305-Full Glue` (`B07FK9BYHW`, 3 x 5 in 2包装): $13.99
* `4A 305-Full Adhesive-300` (`B07QXJZKHC`, 3 x 5 in 5本装 300张): $21.99

### 2. B2B 数量阶梯价格（Quantity Discounts）设定标准
由于满胶系列是当前全店的主力刚需畅销品，库存充足且毛利健康，**切忌大幅打折**：
* **购买 2 ~ 4 件**：享 **3% 折扣**（降低凑单门槛）
* **购买 5 ~ 9 件**：享 **5% 折扣**（针对小型办公团队日常采购）
* **购买 10 件以上**：享 **8% 折扣**（锁定企业大宗批量采购，兼顾高利润）

---

## 七、 广告大盘与每日扣费逻辑

1. **扣费机理**：亚马逊 Sponsored Products 为 CPC（Cost Per Click）点击付费模式，展现不收费，只有买家点击才会扣费。出价提高仅提高搜索结果首页曝光几率，不会导致无点击扣费。
2. **预算大盘**：日预算控制在 **$112 ~ $116**，各主力活动配额明晰，无失控风险。

---

## 八、 新对话交接与执行清单 (Next Action Checklist)

在新开的会话中，直接发送如下指令即可无缝承接：
1. **【最高优先级】变体报告查看**：通过浏览器检查 Feed `287106020763` 的下载处理报告，提取 8 个失败 SKU 的具体错误码并快速修正。
2. **【次高优先级】2028-N 调价**：将 `4A 2028-N-B07DJ-FBM` 改为包邮模板并定价 $9.99，创建对应广告组。
3. **【中优先级】满胶阶梯价录入**：在卖家后台为 6 款满胶热销 SKU 录入 3% / 5% / 8% 的企业阶梯价。
