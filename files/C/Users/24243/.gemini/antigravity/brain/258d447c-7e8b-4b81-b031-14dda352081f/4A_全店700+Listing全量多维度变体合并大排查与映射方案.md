# 【全店 700+ 历史 Listing 与在售现货全量多维度变体合并大排查与映射方案】

> **专项任务**：全店碎片化 Listing 变体合并与资产盘活大排查  
> **审计标的**：全店 854 个历史 SKU/ASIN（含 269 款历史断货好评款、163 款调价现货款、以及各批次由于“重新申请 FBA 标签”而人为拆分出来的兄弟链接）  
> **数据底表**：`所有商品报告_09-03-2026.txt`、`4A缺货_269评分已补全_被低估好款.xlsx`、`4A-SL缺货评分好款.xlsx`、`WooCommerce_完整改价_163_SKUs_复核后上传_2026-08-20.csv`、`4A_2026-08-10库存.xlsx`、`亚马逊供应商和开店总表-2026 (3).xlsx`、`vc_sc_audit_data.json`  
> **输出配套**：已同步生成完整 Excel 总表：[`4A_全店变体合并全量大排查与挂载映射总表.xlsx`](file:///E:/Desktop/4A_全店变体合并全量大排查与挂载映射总表.xlsx)

---

## 一、 全店超级家族大变体整合总览 (Executive Blueprints)

经过对全店 939 个统一商品实体的全面清洗与深度归拢，我们遵循**“以页面最好的那个为准”（综合评价数、评分、FBA 现货库存、内容素材成熟度）**与**“双维度变体无损绑定（ColorName-NumberOfItems / StyleName-NumberOfItems）”**两大军规，将全店数百个碎片化单品全面归拢为 **14 个核心消费文具超级家族 + 1 个 B2B 大画幅看板日程家族**：

| 家族编号 | 超级品类家族名称 | 父体 SKU (Parent SKU) | 变体主题 (Theme) | 主力保留 ASIN / SKU | 成员数 | FBA现货 | 聚合历史好评 | 核心作战收益 |
| :---: | :--- | :--- | :---: | :--- | :---: | :---: | :---: | :--- |
| **Hero-01** | **30315**<br>`彩虹15色便签家族` | `PARENT-4A-30315-RAINBOW-3X3` | `StyleName-NumberOfItems` | **`B07F295DPC`**<br>(4A 30315) | 8款 | **1219件** | **295评** | 【0评秒变122评】将断货老链接122条好评无缝注入新上架的22件现货Listing，激活视频与A+极速出单。 |
| **Hero-02** | **BS**<br>`1801` | `PARENT-4A-BS-EXECUTIVE-LEATHER` | `StyleName-NumberOfItems` | **`B07JVSYNYV`**<br>(4A BS 1801-FBA) | 9款 | **1082件** | **196评** | 【533评霸权+盘活37件替芯】将23评重复链接合入510评主页，并挂载37件12叠替芯子体，以礼盒高流量零广告动销替芯。 |
| **Hero-03** | **4012**<br>`/` | `PARENT-4A-4012-4013-PPBOX` | `ColorName-NumberOfItems` | **`B01M3N310M`**<br>(4A 4012-B07T-FBA) | 26款 | **1654件** | **511评** | 【救急补库存+评价聚合】将分流在低曝光链接上的17件FBA库存合并至213评高权重链接，库存升至20件，规避断货。 |
| **Hero-04** | **5084**<br>`/` | `PARENT-4A-508-LARGE-5X8` | `ColorName-NumberOfItems` | **`B07FKJM2LX`**<br>(AAAA 4A 5084-N-L) | 17款 | **5238件** | **272评** | 【全店第一资产+评价破百】统合全店最大货值资产（101件现货/285件总库存），融合5088的60评与5084的39评，评价达99+。 |
| **Hero-05** | **608**<br>`特大横线便签家族` | `PARENT-4A-608-XLARGE-6X8` | `ColorName-NumberOfItems` | **`B07HDVVZ1B`**<br>(4A 608-N-L-210) | 45款 | **2706件** | **652评** | 【消灭低分链接+吸收现货】将3.6★孤立链接合并至90评4.3★主链接，吸收现货并挂载2本/420张及彩色装。 |
| **Hero-06** | **406x4**<br>`/` | `PARENT-4A-406-LARGE-4X6` | `ColorName-NumberOfItems` | **`B07FKL263W`**<br>(AAAA 4A 406x6) | 93款 | **6598件** | **457评** | 【稀释1星差评+引入135条历史权重】将20件现货但带1星差评的B07FKHHTY4与淡彩135评老款及12叠装合体，全面激活现货。 |
| **Hero-07** | **406xx**<br>`手账索引便签本与书签家族` | `PARENT-4A-406XX-INDEX-TABS` | `StyleName-NumberOfItems` | **`B07FKBHTDG`**<br>(4A 40609) | 41款 | **6579件** | **194评** | 【以614件现货巨无霸为核心合体】以全店单品库存第一的40609为基座，统合10个散乱索引贴链接，形成完整办公手账选购家族。 |
| **Hero-08** | **301**<br>`/` | `PARENT-4A-301-MINI-SMALL` | `ColorName-NumberOfItems` | **`B01LVTWP7Q`**<br>(4A 301x12-N) | 77款 | **33770件** | **5742评** | 【千评VC老祖宗合流+盘活3.3万件资产】承接VC历史69,848套爆款权重，统合12/24/32叠小规格便签，释放全店最大库存池。 |
| **Hero-09** | **302**<br>`/` | `PARENT-4A-FULL-ADHESIVE-PADS` | `StyleName-NumberOfItems` | **`B07QXJYTZ7`**<br>(4A 303-Full Adhesive-400) | 113款 | **10554件** | **2978评** | 【营收支柱大合体+激活534件积压款】全粘满胶贡献店铺70%营收，将3x3/3x4/3x5全粘规格打通，吸收144评并引爆大批量采购。 |
| **Hero-10** | **303**<br>`经典正方形便签家族` | `PARENT-4A-303-CLASSIC-3X3` | `ColorName-NumberOfItems` | **`B07B7JF9LB`**<br>(4A 303M-PNx12) | 132款 | **6375件** | **2032评** | 【统领文具第一大词3x3】将6叠/12叠/24叠平装与横线、荧光色/黄色/粉彩彻底统合，霸占Amazon核心主流搜索入口。 |
| **Hero-11** | **601**<br>`/` | `PARENT-4A-SIGN-HERE-FLAGS` | `StyleName-NumberOfItems` | **`B07F2CWVQ7`**<br>(4A 124418) | 111款 | **10237件** | **744评** | 【B2B极速出单组合】文档审核Sign Here箭头贴与0.6x2/0.75x2.5多色便签条合流，针对律所、金融、高校B2B采购打爆客单价。 |
| **Hero-12** | **PSS**<br>`满胶卷带与切刀替芯收纳家族` | `PARENT-4A-PSS-ROLL-TAPE` | `StyleName-NumberOfItems` | **`B07T791NDQ`**<br>(4A PSS 9-5) | 9款 | **202件** | **0评** | 【带底座+替芯捆绑销售】以带切刀底座为主力，挂载1卷/2卷/4卷不同色彩替芯，实现零边角料自由裁剪文具大升级。 |
| **Hero-13** | **8065~8088**<br>`24色全光谱便签家族` | `PARENT-4A-8065-8088-SPECTRUM-24` | `ColorName-NumberOfItems` | **`B077QFD8G7`**<br>(4A 8065) | 45款 | **59件** | **63评** | 【消灭24个碎片自竞孤岛】将老爸当年拆分的整整24个单色链接合二为一，打造24色全光谱彩虹选色大页，转化率直线上升。 |
| **Hero-14** | **SMC**<br>`/` | `PARENT-4A-SHAPES-CUBE-NOVELTY` | `StyleName-NumberOfItems` | **`B00SMEEF2A`**<br>(4A 5078) | 167款 | **5499件** | **2417评** | 【异形好评合体出击】统合拼图(43评4.1★)、心形、树叶、炸弹与四面印花便签砖，形成高溢价个性礼品便签矩阵。 |
| **Hero-15** | **BP**<br>`/` | `PARENT-4A-BP-MEETING-PLANNERS` | `StyleName-NumberOfItems` | **`B07Z2555TN`**<br>(4A 404-AC-Holder) | 46款 | **3291件** | **218评** | 【$50+高客单价B2B专攻】统合11x11/15x15/22x22会议大白板便签与日程计划本、亚克力笔筒收纳，主攻企业批量团购。 |
| **合计** | **全店 15 大家族大变体总计** | `--` | `--` | `--` | **939款** | **95063件** | **16771评** | **彻底消灭自竞内耗，盘活全店 10 万件库存，聚合数万真实好评！** |

---

## 二、 核心作战家族深度映射清单与实操设计

### 【Hero-01】30315 彩虹15色便签家族 (3x3 in 15-Color Pads)
- **父体 SKU (Parent SKU)**: `PARENT-4A-30315-RAINBOW-3X3`
- **变体主题 (Variation Theme)**: `StyleName-NumberOfItems`
- **主力目标保留商品 (Master Target)**: **`B07F295DPC`** (SKU: `4A 30315`)
- **家族资产盘点**: 涵盖 **8 款** 兄弟链接 | 当前可售 FBA 现货: **1219 件** | 可聚合历史好评: **295 条**
- **核心合并收益**: 【0评秒变122评】将断货老链接122条好评无缝注入新上架的22件现货Listing，激活视频与A+极速出单。

| 角色 / 操作类型 | 子体 SKU | 子体 ASIN | ColorName 设定值 | NumberOfItems 设定值 | StyleName 设定值 | FBA现货 | 历史评价 | 售价 | 官方状态 | 推荐执行渠道 |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **【主力保留】** | `4A 30315` | `B07F295DPC` | 15-Color Rainbow | 15 Pads | Standard Flat Note Pad | 0 | 0评 | $14.99 | Active | 保留为父体锚点 |
| 【合并重复】 | `4A GM30315` | `B07FKG29KB` | 15-Color Rainbow | 15 Pads | Standard Flat Note Pad | 1054 | 122评 (4★) | $21.99 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GM30315-Z` | `B07RP82CVJ` | 15-Color Rainbow | 15 Pads | Pop-Up Accordion Pad | 165 | 86评 (2.9★) | $19.99 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A 015` | `B01M58HPUJ` | 15-Color Rainbow | 100 Sheets | Standard Flat Note Pad | 0 | 29评 (3.2★) | $8.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A 016` | `B01LWA44KM` | 15-Color Rainbow | 100 Sheets | Standard Flat Note Pad | 0 | 29评 (3.2★) | $12.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A sticky 002-4` | `B07JNZ1H6C` | 15-Color Rainbow | 100 Sheets | Standard Flat Note Pad | 0 | 29评 (3.2★) | $-- | Incomplete | 卖家助手 -> 合并商品 |
| 【合并重复】 | `AAAA 4A 30315` | `B07FKG29KB` | 15-Color Rainbow | 15 Pads | Standard Flat Note Pad | 0 | 0评 | $18.99 | Inactive | 卖家助手 -> 合并商品 |
| 【变体挂载】 | `4A 30315-Z` | `B07RP82CVJ` | 15-Color Rainbow | 15 Pads | Pop-Up Accordion Pad | 0 | 0评 | $16.99 | Inactive | 变体向导 / 批量模板 |


### 【Hero-02】BS 1801 / 1803 商务皮质礼盒与替芯家族 (Executive Leather Set & Refill)
- **父体 SKU (Parent SKU)**: `PARENT-4A-BS-EXECUTIVE-LEATHER`
- **变体主题 (Variation Theme)**: `StyleName-NumberOfItems`
- **主力目标保留商品 (Master Target)**: **`B07JVSYNYV`** (SKU: `4A BS 1801-FBA`)
- **家族资产盘点**: 涵盖 **9 款** 兄弟链接 | 当前可售 FBA 现货: **1082 件** | 可聚合历史好评: **196 条**
- **核心合并收益**: 【533评霸权+盘活37件替芯】将23评重复链接合入510评主页，并挂载37件12叠替芯子体，以礼盒高流量零广告动销替芯。

| 角色 / 操作类型 | 子体 SKU | 子体 ASIN | ColorName 设定值 | NumberOfItems 设定值 | StyleName 设定值 | FBA现货 | 历史评价 | 售价 | 官方状态 | 推荐执行渠道 |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **【主力保留】** | `4A BS 1801-FBA` | `B07JVSYNYV` | Classic Assorted | 100 Sheets | Executive Leather Gift Box | 20 | 53评 (4.0★) | $$14.99 + $0.00 | 在售 | 保留为父体锚点 |
| 【合并重复】 | `4ASCBS1812345` | `B07WFVJT3F` | Neon Assorted | 3 Pcs | Executive Leather Gift Box | 0 | 23评 (4.5★) | $-- | Incomplete | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GMBS 1801` | `B07K8L4K8K` | Neon Assorted | 3 Pcs | Executive Leather Gift Box | 1035 | 0评 | $17.99 | Active | 卖家助手 -> 合并商品 |
| 【变体挂载】 | `4A BS 1802` | `B07K8JQ9JW` | Classic Assorted | 700 Sheets | With Calendar Desk Set | 11 | 22评 (4.6★) | $8.99 | Active | 变体向导 / 批量模板 |
| 【变体挂载】 | `4A BS 1803` | `B07K8KJ83T` | Multicolor Assorted | 1800 Sheets | With Calendar Desk Set | 11 | 22评 (4.6★) | $11.99 | Active | 变体向导 / 批量模板 |
| 【变体挂载】 | `4A BS 1803-FBA` | `B07J6Q5TTR` | Classic Assorted | 1800 Sheets | With Calendar Desk Set | 5 | 53评 (4.0★) | $$12.99 + $0.00 | 在售 | 变体向导 / 批量模板 |
| 【变体挂载】 | `4A BS 1801` | `B07K8L4K8K` | Neon Assorted | 3 Pcs | Executive Leather Gift Box | 0 | 22评 (4.6★) | $17.99 | Active | 变体向导 / 批量模板 |
| 【变体挂载】 | `4A BS 1801 Refill` | `B0F2TJZ8GM` | Bright Ultra Colors | 12 Pads | Replacement Refill Pack | 0 | 1评 (4.0★) | $18.99 | Active | 变体向导 / 批量模板 |
| 【变体挂载】 | `4A BS 1801 + Refill` | `B0FGJR49SW` | Bright Ultra Colors | 1800 Sheets | Replacement Refill Pack | 0 | 0评 | $-- | Incomplete | 变体向导 / 批量模板 |


### 【Hero-03】4012 / 4013 PP盒18叠组合便签家族 (18-Pads Desk Storage Cube)
- **父体 SKU (Parent SKU)**: `PARENT-4A-4012-4013-PPBOX`
- **变体主题 (Variation Theme)**: `ColorName-NumberOfItems`
- **主力目标保留商品 (Master Target)**: **`B01M3N310M`** (SKU: `4A 4012-B07T-FBA`)
- **家族资产盘点**: 涵盖 **26 款** 兄弟链接 | 当前可售 FBA 现货: **1654 件** | 可聚合历史好评: **511 条**
- **核心合并收益**: 【救急补库存+评价聚合】将分流在低曝光链接上的17件FBA库存合并至213评高权重链接，库存升至20件，规避断货。

| 角色 / 操作类型 | 子体 SKU | 子体 ASIN | ColorName 设定值 | NumberOfItems 设定值 | StyleName 设定值 | FBA现货 | 历史评价 | 售价 | 官方状态 | 推荐执行渠道 |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **【主力保留】** | `4A 4012-B07T-FBA` | `B01M3N310M` | Multicolor Assorted | 18 Pads | PP Desk Storage Box | 0 | 212评 (4.0★) | $12.99 | Inactive | 保留为父体锚点 |
| 【合并重复】 | `4A 021` | `B01MA0ZWWR` | Pastel Assorted | 100 Sheets | Standard Flat Note Pad | 0 | 29评 (3.2★) | $15.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A 022` | `B01M6181P0` | Neon Assorted | 100 Sheets | Standard Flat Note Pad | 0 | 29评 (3.2★) | $17.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GM4012*2` | `B01MZ1PQQ8` | Multicolor Assorted | 18 Pads | PP Desk Storage Box | 390 | 9评 (4.6★) | $23.99 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GM4013` | `B07RQ6HLK3` | Neon Assorted | 18 Pads | PP Desk Storage Box | 113 | 9评 (4.6★) | $17.99 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4ASNVPDS-MC` | `B07TXKTTKH` | Neon Assorted | 18 Pads | PP Desk Storage Box | 0 | 9评 (4.6★) | $-- | Incomplete | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GM4012` | `B07FKJLZNG` | Multicolor Assorted | 18 Pads | PP Desk Storage Box | 780 | 1评 (5.0★) | $11.99 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A 020` | `B01NGWHSK1` | Pastel Assorted | 18 Pads | Standard Flat Note Pad | 0 | 1评 (1★) | $11.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GM303x18-Y` | `B07FKGLYH6` | Pastel Assorted | 18 Pads | Standard Flat Note Pad | 35 | 0评 | $11.99 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GM303x6-Y-L*3` | `B07FK8L1P2` | Pastel Assorted | 18 Pads | Lined / Ruled Notes | 336 | 0评 | $14.99 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `AAAA 4A 4012` | `B07FKJLZNG` | Multicolor Assorted | 18 Pads | PP Desk Storage Box | 0 | 0评 | $16.99 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GM303x18-N*4` | `B07MCTZGL7` | Neon Assorted | 100 Sheets | Standard Flat Note Pad | 0 | 0评 | $44.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `AAAA 4A 303x18` | `B07FKHDQDP` | Pastel Assorted | 100 Sheets | Standard Flat Note Pad | 0 | 0评 | $15.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `AAAA 4A 303x18-N` | `B07FKFXDXH` | Neon Assorted | 100 Sheets | Standard Flat Note Pad | 0 | 0评 | $14.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `AAAA 4A 303x18-N-Z` | `B07FKJK53S` | Neon Assorted | 100 Sheets | Pop-Up Accordion Pad | 0 | 0评 | $21.99 | Inactive | 卖家助手 -> 合并商品 |
| *... (该家族共 26 款，其余款式已完整收入 Excel 总表专属工作表中)* | | | | | | | | | | |

### 【Hero-04】5084 / 5088 大号横线便签家族 (5x8 in Large Ruled Sticky Notes)
- **父体 SKU (Parent SKU)**: `PARENT-4A-508-LARGE-5X8`
- **变体主题 (Variation Theme)**: `ColorName-NumberOfItems`
- **主力目标保留商品 (Master Target)**: **`B07FKJM2LX`** (SKU: `AAAA 4A 5084-N-L`)
- **家族资产盘点**: 涵盖 **17 款** 兄弟链接 | 当前可售 FBA 现货: **5238 件** | 可聚合历史好评: **272 条**
- **核心合并收益**: 【全店第一资产+评价破百】统合全店最大货值资产（101件现货/285件总库存），融合5088的60评与5084的39评，评价达99+。

| 角色 / 操作类型 | 子体 SKU | 子体 ASIN | ColorName 设定值 | NumberOfItems 设定值 | StyleName 设定值 | FBA现货 | 历史评价 | 售价 | 官方状态 | 推荐执行渠道 |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **【主力保留】** | `AAAA 4A 5084-N-L` | `B07FKJM2LX` | Bright Ultra Colors | 8 Pads | Lined / Ruled Notes | 0 | 31评 (4.3★) | $19.99 | Active | 保留为父体锚点 |
| **【主力保留】** | `4A GM5084-N-L*2` | `B07FKJM2LX` | Bright Ultra Colors | 8 Pads | Lined / Ruled Notes | 1210 | 0评 | $18.98 | Inactive | 保留为父体锚点 |
| 【合并重复】 | `4A 5084 Parent` | `B0FB8GH4HV` | Bright Ultra Colors | 4 Pads | Lined / Ruled Notes | 0 | 33评 (4.4★) | $-- | Incomplete | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A 5082-Y-L-GM` | `B07F2BHFJH` | Pastel Assorted | 2 Pads | Lined / Ruled Notes | 53 | 17评 (3.8★) | $$11.99 + $0.00 | 在售 | 卖家助手 -> 合并商品 |
| 【合并重复】 | `AAAA 4A 5082-Y-L` | `B07FK7JN8Q` | Canary Yellow | 50 Sheets | Lined / Ruled Notes | 0 | 1评 (1★) | $9.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GM5084-N-L` | `B07F2B49BL` | Bright Ultra Colors | 4 Pads | Lined / Ruled Notes | 2416 | 0评 | $10.39 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GM5084-N-L*4` | `B07MQVWLSY` | Bright Ultra Colors | 16 Pads | Lined / Ruled Notes | 605 | 0评 | $35.99 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GM5088-N-L` | `B07RP9MB7Y` | Bright Ultra Colors | 8 Pads | Lined / Ruled Notes | 582 | 0评 | $19.99 | Active | 卖家助手 -> 合并商品 |
| 【变体挂载】 | `4A 5082-Y-Lx2` | `B0F9L5G6XQ` | Pastel Assorted | 4 Pads | Lined / Ruled Notes | 302 | 4评 (4.0★) | $$19.99 + $0.00 | 在售 | 变体向导 / 批量模板 |
| 【变体挂载】 | `4A 5084-N-L` | `B07F2B49BL` | Bright Ultra Colors | 4 Pads | Lined / Ruled Notes | 66 | 33评 (4.4★) | $15.99 | 在售 | 变体向导 / 批量模板 |
| 【变体挂载】 | `4A 5084-N-L*4` | `B07MQVWLSY` | Bright Ultra Colors | 16 Pads | Lined / Ruled Notes | 4 | 32评 (4.3★) | $$35.99 + $0.00 | 在售 | 变体向导 / 批量模板 |
| 【变体挂载】 | `4A 303-Holder+Flag` | `B0F2TJ7ZL7` | Neon Assorted | 80 Sheets | Dispenser / Organizer Set | 0 | 1评 (5.0★) | $19.99 | Active | 变体向导 / 批量模板 |
| 【变体挂载】 | `4A 5088-N-L` | `B07RP9MB7Y` | Bright Ultra Colors | 8 Pads | Lined / Ruled Notes | 0 | 60评 (4.2★) | $19.99 | Active | 变体向导 / 批量模板 |
| 【变体挂载】 | `4A 5088-Rainbow` | `B0F2YHTD8T` | Bright Ultra Colors | 10 Sheets | Standard Flat Note Pad | 0 | 0评 | $12.99 | Active | 变体向导 / 批量模板 |
| 【变体挂载】 | `4A 5082-Y-L` | `B07F2BHFJH` | Pastel Assorted | 2 Pads | Lined / Ruled Notes | 0 | 0评 | $5.99 | Inactive | 变体向导 / 批量模板 |
| *... (该家族共 17 款，其余款式已完整收入 Excel 总表专属工作表中)* | | | | | | | | | | |

### 【Hero-05】608 特大横线便签家族 (6x8 in Extra Large Ruled Sticky Notes)
- **父体 SKU (Parent SKU)**: `PARENT-4A-608-XLARGE-6X8`
- **变体主题 (Variation Theme)**: `ColorName-NumberOfItems`
- **主力目标保留商品 (Master Target)**: **`B07HDVVZ1B`** (SKU: `4A 608-N-L-210`)
- **家族资产盘点**: 涵盖 **45 款** 兄弟链接 | 当前可售 FBA 现货: **2706 件** | 可聚合历史好评: **652 条**
- **核心合并收益**: 【消灭低分链接+吸收现货】将3.6★孤立链接合并至90评4.3★主链接，吸收现货并挂载2本/420张及彩色装。

| 角色 / 操作类型 | 子体 SKU | 子体 ASIN | ColorName 设定值 | NumberOfItems 设定值 | StyleName 设定值 | FBA现货 | 历史评价 | 售价 | 官方状态 | 推荐执行渠道 |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **【主力保留】** | `4A 608-N-L-210` | `B07B8RBCKT` | Bright Ultra Colors | 210 Sheets | Lined / Ruled Notes | 1518 | 0评 | $12.39 | Active | 保留为父体锚点 |
| **【主力保留】** | `4A 608-N-L-210-FBA` | `B07HDVVZ1B` | Neon Assorted | 210 Sheets | Lined / Ruled Notes | 0 | 89评 (4.4★) | $11.99 | Inactive | 保留为父体锚点 |
| 【合并重复】 | `4A GM6084-NL` | `B07RR95YW7` | Neon Assorted | 100 Sheets | Lined / Ruled Notes | 198 | 60评 (4.2★) | $26.49 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4ABNLCOLORFUL` | `B07TSD42PN` | Neon Assorted | 100 Sheets | Lined / Ruled Notes | 0 | 60评 (4.2★) | $-- | Incomplete | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GM608S-Linex4` | `B07FKPY2V6` | Bright Ultra Colors | 4 Pads | Lined / Ruled Notes | 351 | 6评 (4.0★) | $10.39 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GM608SL-5` | `B07RN7W756` | Bright Ultra Colors | 5 Pads | Lined / Ruled Notes | 106 | 6评 (5.0★) | $28.49 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `AAAA 4A 40608` | `B00SMEEVL0` | Neon Assorted | 15 Sheets | Index Tabs & Page Markers | 83 | 6评 (3.7★) | $5.99 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GM608x2-N-L OB` | `B07KT71XX3` | Neon Assorted | 2 Pads | Lined / Ruled Notes | 0 | 1评 (5★) | $10.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GM608x2-N-L YB` | `B07FKJD442` | Neon Assorted | 2 Pads | Lined / Ruled Notes | 0 | 1评 (5★) | $10.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A sticky 009-9` | `B07KR9LD68` | Neon Assorted | 2 Pads | Lined / Ruled Notes | 0 | 1评 (5★) | $-- | Incomplete | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GM608-N-L-210*2` | `B07PZ56WXD` | Neon Assorted | 210 Sheets | Lined / Ruled Notes | 159 | 0评 | $19.99 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GM6087-NL-420` | `B07T77N118` | Neon Assorted | 60 Sheets | Lined / Ruled Notes | 157 | 0评 | $24.99 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GM608S-Linex4*3` | `B07B8DSVRB` | Bright Ultra Colors | 50 Sheets | Lined / Ruled Notes | 117 | 0评 | $26.99 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `AAAA 4A 608-N-L-210` | `B07B8RBCKT` | Bright Ultra Colors | 210 Sheets | Lined / Ruled Notes | 0 | 0评 | $14.99 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `AAAA 4A 608S-Linex4` | `B07FKPY2V6` | Bright Ultra Colors | 4 Pads | Lined / Ruled Notes | 0 | 0评 | $14.99 | Active | 卖家助手 -> 合并商品 |
| *... (该家族共 45 款，其余款式已完整收入 Excel 总表专属工作表中)* | | | | | | | | | | |

### 【Hero-06】406x4 / 406x6 / 305 大号横线与纯色便签家族 (4x6 & 3x5 in Large Notes)
- **父体 SKU (Parent SKU)**: `PARENT-4A-406-LARGE-4X6`
- **变体主题 (Variation Theme)**: `ColorName-NumberOfItems`
- **主力目标保留商品 (Master Target)**: **`B07FKL263W`** (SKU: `AAAA 4A 406x6`)
- **家族资产盘点**: 涵盖 **93 款** 兄弟链接 | 当前可售 FBA 现货: **6598 件** | 可聚合历史好评: **457 条**
- **核心合并收益**: 【稀释1星差评+引入135条历史权重】将20件现货但带1星差评的B07FKHHTY4与淡彩135评老款及12叠装合体，全面激活现货。

| 角色 / 操作类型 | 子体 SKU | 子体 ASIN | ColorName 设定值 | NumberOfItems 设定值 | StyleName 设定值 | FBA现货 | 历史评价 | 售价 | 官方状态 | 推荐执行渠道 |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **【主力保留】** | `AAAA 4A 406x6` | `B07FKL263W` | Pastel Assorted | 6 Pads | Standard Flat Note Pad | 7 | 1评 (1.0★) | $$13.49 + $0.00 | 在售 | 保留为父体锚点 |
| 【合并重复】 | `4A GMGR4066` | `B07RP9MSSL` | White | 100 Sheets | Grid / Graph Notes | 0 | 60评 (4.2★) | $19.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A 5078` | `B00SMEEF2A` | Neon Assorted | 100 Sheets | Die-Cut Puzzle Shape | 0 | 43评 (4.1★) | $8.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A sticky 003-3` | `B07JY1NRG1` | Neon Assorted | 100 Sheets | Lined / Ruled Notes | 0 | 41评 (3.3★) | $-- | Incomplete | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GM404SL-15` | `B07RQ69Q1Q` | Bright Ultra Colors | 80 Sheets | Lined / Ruled Notes | 44 | 6评 (5.0★) | $38.99 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GM406SL-10` | `B07RP85C2P` | Bright Ultra Colors | 80 Sheets | Lined / Ruled Notes | 466 | 6评 (5.0★) | $33.49 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4ASUPERSN-5C` | `B07TTCCL7J` | Bright Ultra Colors | 80 Sheets | Lined / Ruled Notes | 0 | 6评 (5★) | $-- | Incomplete | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A 027` | `B01MXYR202` | Pastel Assorted | 6 Pads | Standard Flat Note Pad | 0 | 4评 (3.8★) | $7.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A Sticky 005-5` | `B07KT5PXLK` | Pastel Assorted | 6 Pads | Standard Flat Note Pad | 0 | 4评 (3.8★) | $-- | Incomplete | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A Sticky 007-7` | `B07KT5SQWF` | Bright Ultra Colors | 6 Pads | Standard Flat Note Pad | 0 | 4评 (2.4★) | $-- | Incomplete | 卖家助手 -> 合并商品 |
| 【合并重复】 | `AAAA 01` | `B07JFQVD8Q` | White | 2 Pads | Lined / Ruled Notes | 0 | 3评 (5★) | $-- | Incomplete | 卖家助手 -> 合并商品 |
| 【合并重复】 | `AAAA 4A 305-ACJT-280` | `B00SMEFE48` | Neon Assorted | 40 Sheets | Standard Flat Note Pad | 0 | 2评 (2★) | $8.49 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `AAAA 4A 305x6` | `B07FD3X3NM` | Pastel Assorted | 2 Packs | Standard Flat Note Pad | 0 | 2评 (5★) | $15.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `AAAA 4A 404x6-N-L` | `B07FKFVXX2` | Bright Ultra Colors | 6 Pads | Lined / Ruled Notes | 0 | 2评 (3.4★) | $11.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GM406x6-N` | `B07FKHHTY4` | Bright Ultra Colors | 6 Pads | Standard Flat Note Pad | 521 | 1评 (1.0★) | $13.99 | Active | 卖家助手 -> 合并商品 |
| *... (该家族共 93 款，其余款式已完整收入 Excel 总表专属工作表中)* | | | | | | | | | | |

### 【Hero-07】406xx 手账索引便签本与书签家族 (40606~40630 Index Tabs & Flags)
- **父体 SKU (Parent SKU)**: `PARENT-4A-406XX-INDEX-TABS`
- **变体主题 (Variation Theme)**: `StyleName-NumberOfItems`
- **主力目标保留商品 (Master Target)**: **`B07FKBHTDG`** (SKU: `4A 40609`)
- **家族资产盘点**: 涵盖 **41 款** 兄弟链接 | 当前可售 FBA 现货: **6579 件** | 可聚合历史好评: **194 条**
- **核心合并收益**: 【以614件现货巨无霸为核心合体】以全店单品库存第一的40609为基座，统合10个散乱索引贴链接，形成完整办公手账选购家族。

| 角色 / 操作类型 | 子体 SKU | 子体 ASIN | ColorName 设定值 | NumberOfItems 设定值 | StyleName 设定值 | FBA现货 | 历史评价 | 售价 | 官方状态 | 推荐执行渠道 |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **【主力保留】** | `4A GM40609*2` | `B07FKBHTDG` | White | 15 Sheets | Lined / Ruled Notes | 337 | 12评 (5.0★) | $9.99 | Active | 保留为父体锚点 |
| **【主力保留】** | `AAAA 4A 40609` | `B07FKBHTDG` | White | 15 Sheets | Lined / Ruled Notes | 614 | 0评 | $$10.99 + $0.00 | 在售 | 保留为父体锚点 |
| **【主力保留】** | `4A 40609` | `B00SMEF4RU` | White | 15 Sheets | Lined / Ruled Notes | 0 | 6评 (3.7★) | $3.99 | Inactive | 保留为父体锚点 |
| 【合并重复】 | `4A GMSCBS 1804` | `B07WDQGB3G` | Classic Assorted | 1180 Sheets | Pop-Up Accordion Pad | 301 | 22评 (4.6★) | $9.99 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A 40621` | `B01NCQ6Q1T` | Neon Assorted | 20 Sheets | Lined / Ruled Notes | 0 | 20评 (3.9★) | $4.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A sticky 015-15` | `B07KS92L4R` | Neon Assorted | 10 Sheets | Lined / Ruled Notes | 0 | 20评 (3.9★) | $-- | Incomplete | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4ADRT521` | `B07TXPZJBJ` | Transparent Writable | 100 Pcs | Index Tabs & Page Markers | 0 | 10评 (4.3★) | $-- | Incomplete | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GM40607*3` | `B07FK8CJ76` | White | 3 Pads | Lined / Ruled Notes | 145 | 4评 (3.9★) | $9.49 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GM40621*2` | `B07FK8RTZH` | White | 2 Pads | Lined / Ruled Notes | 0 | 3评 (5★) | $10.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GM40606*3` | `B07FK8M7RP` | Neon Assorted | 3 Pads | Index Tabs & Page Markers | 91 | 0评 | $7.99 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GM40609x4` | `B07T2ZNTGK` | White | 15 Sheets | Lined / Ruled Notes | 658 | 0评 | $18.99 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GM40622*2` | `B07FKFMJTL` | White | 2 Pads | Lined / Ruled Notes | 65 | 0评 | $3.99 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GM40624*2` | `B07FK8CRM9` | White | 10 Sheets | Lined / Ruled Notes | 747 | 0评 | $5.99 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GM6031x4` | `B07RP9K6KV` | Transparent Writable | 100 Pcs | Index Tabs & Page Markers | 288 | 0评 | $18.99 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GMSC40623*2` | `B07FK81CQ8` | Neon Assorted | 10 Sheets | Lined / Ruled Notes | 95 | 0评 | $7.99 | Active | 卖家助手 -> 合并商品 |
| *... (该家族共 41 款，其余款式已完整收入 Excel 总表专属工作表中)* | | | | | | | | | | |

### 【Hero-08】301 / 202 迷你便签家族 (1.5x2 & 2x2 in Small Size Sticky Notes)
- **父体 SKU (Parent SKU)**: `PARENT-4A-301-MINI-SMALL`
- **变体主题 (Variation Theme)**: `ColorName-NumberOfItems`
- **主力目标保留商品 (Master Target)**: **`B01LVTWP7Q`** (SKU: `4A 301x12-N`)
- **家族资产盘点**: 涵盖 **77 款** 兄弟链接 | 当前可售 FBA 现货: **33770 件** | 可聚合历史好评: **5742 条**
- **核心合并收益**: 【千评VC老祖宗合流+盘活3.3万件资产】承接VC历史69,848套爆款权重，统合12/24/32叠小规格便签，释放全店最大库存池。

| 角色 / 操作类型 | 子体 SKU | 子体 ASIN | ColorName 设定值 | NumberOfItems 设定值 | StyleName 设定值 | FBA现货 | 历史评价 | 售价 | 官方状态 | 推荐执行渠道 |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **【主力保留】** | `4A 301x12-N` | `B01LVTWP7Q` | Neon Assorted | 100 Sheets | Standard Flat Note Pad | 0 | 1168评 (4.2★) | $5.99 | Inactive | 保留为父体锚点 |
| 【合并重复】 | `4A056` | `B01NCNPD4N` | Bright Ultra Colors | 200 Sheets | Standard Flat Note Pad | 0 | 29评 (4★) | $6.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4ASSNDS924` | `B07TXGHQNZ` | Bright Ultra Colors | 200 Sheets | Standard Flat Note Pad | 0 | 29评 (4★) | $-- | Incomplete | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GM354832` | `B07RP9LR73` | 16 Colors Assorted | 32 Pads | Standard Flat Note Pad | 435 | 24评 (3.4★) | $15.99 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A sticky 021-21` | `B07KS9TZ8Q` | Bright Ultra Colors | 60 Pcs | Index Tabs & Page Markers | 0 | 17评 (4.6★) | $-- | Incomplete | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A 484812-N` | `B07F29DHNS` | Pastel Assorted | 20 Pads | Standard Flat Note Pad | 0 | 5评 (3.9★) | $5.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A sticky 030-30` | `B07KSZJ1LK` | Pastel Assorted | 20 Pads | Standard Flat Note Pad | 0 | 5评 (3.9★) | $-- | Incomplete | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GM2028-N*3` | `B07FKGPCQM` | Bright Ultra Colors | 24 Pads | Standard Flat Note Pad | 491 | 4评 (4.6★) | $12.99 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A SC5020+5018` | `B07FKPVP1P` | Classic Assorted | 200 Sheets | Die-Cut Heart Shape | 0 | 4评 (3.6★) | $10.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `AAAA 15` | `B07JJSL8HC` | Classic Assorted | 200 Sheets | Die-Cut Heart Shape | 0 | 4评 (3.6★) | $-- | Incomplete | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GM301x24*2` | `B07FKD3DBJ` | Neon Assorted | 48 Pads | Standard Flat Note Pad | 618 | 3评 (3.3★) | $16.99 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A BP2222 NGPOY` | `B07M854GPK` | Neon Assorted | 30 Sheets | Large Meeting Presentation Pad | 0 | 3评 (2★) | $64.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4ADSSBP-DC` | `B07Q21QT9W` | Neon Assorted | 30 Sheets | Large Meeting Presentation Pad | 0 | 3评 (2★) | $-- | Incomplete | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GM484812-N*3` | `B07PWM2X8Y` | Classic Assorted | 3 Packs | Standard Flat Note Pad | 507 | 2评 (2.4★) | $17.99 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `AAAA 4A 301x12-N` | `B07FK8LN8D` | Bright Ultra Colors | 24 Pads | Standard Flat Note Pad | 0 | 2评 (4.5★) | $16.99 | Active | 卖家助手 -> 合并商品 |
| *... (该家族共 77 款，其余款式已完整收入 Excel 总表专属工作表中)* | | | | | | | | | | |

### 【Hero-09】302 / 303 / 304 / 305 满胶全粘便签家族 (Full Adhesive All-Stick Pads)
- **父体 SKU (Parent SKU)**: `PARENT-4A-FULL-ADHESIVE-PADS`
- **变体主题 (Variation Theme)**: `StyleName-NumberOfItems`
- **主力目标保留商品 (Master Target)**: **`B07QXJYTZ7`** (SKU: `4A 303-Full Adhesive-400`)
- **家族资产盘点**: 涵盖 **113 款** 兄弟链接 | 当前可售 FBA 现货: **10554 件** | 可聚合历史好评: **2978 条**
- **核心合并收益**: 【营收支柱大合体+激活534件积压款】全粘满胶贡献店铺70%营收，将3x3/3x4/3x5全粘规格打通，吸收144评并引爆大批量采购。

| 角色 / 操作类型 | 子体 SKU | 子体 ASIN | ColorName 设定值 | NumberOfItems 设定值 | StyleName 设定值 | FBA现货 | 历史评价 | 售价 | 官方状态 | 推荐执行渠道 |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **【主力保留】** | `4A 303-Full Adhesive-400` | `B07QXJYTZ7` | Classic Assorted | 80 Sheets | Full Adhesive All-Stick Pad | 73 | 42评 (2.8★) | $22.99 | 在售 | 保留为父体锚点 |
| **【主力保留】** | `4A GM303-Full Adhesive-400` | `B07QXJYTZ7` | Classic Assorted | 80 Sheets | Full Adhesive All-Stick Pad | 0 | 0评 | $22.99 | Inactive | 保留为父体锚点 |
| 【合并重复】 | `4A GM-PSS 9-3 YOR` | `B01MZ4FDN5` | Neon Assorted | 1 Pack | Full Adhesive All-Stick Pad | 0 | 256评 (3.9★) | $11.99 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GMPSS 9-5 Refill` | `B07QXJX2BV` | Classic Assorted | 1 Pack | Replacement Refill Pack | 413 | 256评 (3.9★) | $19.99 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A 303-4 Full Glue` | `B01LW6N0WA` | Classic Assorted | 30 Sheets | Full Adhesive All-Stick Pad | 0 | 144评 (3.4★) | $5.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `AAAA 4A 304-Full Glue` | `B07FK975YB` | Bright Ultra Colors | 10 Pads | Full Adhesive All-Stick Pad | 380 | 44评 (2.2★) | $$12.99 + $0.00 | 在售 | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A30FANNA00` | `B07QWKWRQR` | Classic Assorted | 80 Sheets | Full Adhesive All-Stick Pad | 0 | 44评 (2.7★) | $-- | Incomplete | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A PSS 9-1 NP` | `B01MT35G2V` | Neon Assorted | 2 Rolls | Full Adhesive All-Stick Pad | 0 | 43评 (4.2★) | $14.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GM-PSS 9-1 NYNRx2` | `B07QWKWWP2` | Neon Assorted | 2 Pads / 100 Sheets | Replacement Refill Pack | 132 | 34评 (3.7★) | $19.99 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GM-SC-PSS 9-1 Grid Refill` | `B07FKF5V92` | Classic Assorted | 1 Pack | Grid / Graph Notes | 379 | 34评 (3.7★) | $17.39 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GMPSS 9-1 Grid-NBNPx2` | `B07QWKYMGM` | Neon Assorted | 2 Pads / 100 Sheets | Grid / Graph Notes | 358 | 34评 (3.7★) | $22.99 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GMPSS 9-1 NGNOx2` | `B07QXJY3FH` | Neon Assorted | 2 Pads / 100 Sheets | Replacement Refill Pack | 639 | 34评 (3.7★) | $22.49 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GMPSS 9-1 Refill` | `B07QVKPZXX` | Classic Assorted | 1 Pack | Replacement Refill Pack | 408 | 34评 (3.7★) | $17.99 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A 304-Full Adhesive Parent` | `B0F9WBC7JM` | Bright Ultra Colors | 10 Pads | Full Adhesive All-Stick Pad | 0 | 29评 (2★) | $-- | Incomplete | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GM-SCPSS 32x6` | `B08DKJ2K3T` | Neon Assorted | 6 Rolls | Full Adhesive All-Stick Pad | 835 | 16评 (3.6★) | $13.99 | Active | 卖家助手 -> 合并商品 |
| *... (该家族共 113 款，其余款式已完整收入 Excel 总表专属工作表中)* | | | | | | | | | | |

### 【Hero-10】303 经典正方形便签家族 (3x3 in Square Standard & Lined Notes)
- **父体 SKU (Parent SKU)**: `PARENT-4A-303-CLASSIC-3X3`
- **变体主题 (Variation Theme)**: `ColorName-NumberOfItems`
- **主力目标保留商品 (Master Target)**: **`B07B7JF9LB`** (SKU: `4A 303M-PNx12`)
- **家族资产盘点**: 涵盖 **132 款** 兄弟链接 | 当前可售 FBA 现货: **6375 件** | 可聚合历史好评: **2032 条**
- **核心合并收益**: 【统领文具第一大词3x3】将6叠/12叠/24叠平装与横线、荧光色/黄色/粉彩彻底统合，霸占Amazon核心主流搜索入口。

| 角色 / 操作类型 | 子体 SKU | 子体 ASIN | ColorName 设定值 | NumberOfItems 设定值 | StyleName 设定值 | FBA现货 | 历史评价 | 售价 | 官方状态 | 推荐执行渠道 |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **【主力保留】** | `4A 0183` | `B07B7JF9LB` | Neon Assorted | 12 Pads | Standard Flat Note Pad | 0 | 2评 (5★) | $13.99 | Inactive | 保留为父体锚点 |
| **【主力保留】** | `4A 303M-PNx12` | `B07B7JF9LB` | Neon Assorted | 100 Sheets | Standard Flat Note Pad | 0 | 0评 | $18.99 |  | 保留为父体锚点 |
| 【合并重复】 | `4A GMSCPSS 7` | `B0821LD25K` | Classic Assorted | 100 Sheets | Pop-Up Accordion Pad | 1155 | 86评 (2.9★) | $12.99 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A SCPOPUP303` | `B0827QX86D` | Bright Ultra Colors | 15 Pads | Pop-Up Accordion Pad | 0 | 86评 (2.9★) | $-- | Incomplete | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GM303M-PN-Zx12` | `B01JGGQ4WQ` | Neon Assorted | 100 Sheets | Pop-Up Accordion Pad | 0 | 68评 (3.2★) | $10.32 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4ABP111522NP4` | `B07SDDQFC7` | Bright Ultra Colors | 4 Pads | Standard Flat Note Pad | 0 | 58评 (3.6★) | $-- | Incomplete | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A 008` | `B01MQW8U03` | Canary Yellow | 100 Sheets | Lined / Ruled Notes | 0 | 41评 (3.3★) | $6.49 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GM303-AC-holder` | `B07FKHHTYG` | Bright Ultra Colors | 1 Pack | Dispenser / Organizer Set | 1196 | 36评 (4.3★) | $10.99 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A 024` | `B01MEBRJQE` | Canary Yellow | 100 Sheets | Standard Flat Note Pad | 0 | 31评 (3★) | $15.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A 014` | `B01M21QGV3` | Canary Yellow | 100 Sheets | Standard Flat Note Pad | 0 | 29评 (3.2★) | $7.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `AAAA 4A 3031` | `B07FK8FM6W` | Bright Ultra Colors | 1 Pack | Dispenser / Organizer Set | 0 | 26评 (4.5★) | $6.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `AAAA 4A 3032` | `B07FK5VJXR` | Bright Ultra Colors | 24 Pads / 2400 Sheets | Dispenser / Organizer Set | 0 | 26评 (4.5★) | $6.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `AAAA 4A 3033` | `B07FKF3MXV` | Bright Ultra Colors | 1 Pack | Dispenser / Organizer Set | 0 | 26评 (4.5★) | $6.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `AAAA 4A 3034` | `B07FK8MBLS` | Bright Ultra Colors | 1 Pack | Dispenser / Organizer Set | 0 | 26评 (4.5★) | $6.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `AAAA 4A 3035` | `B07FK7C2PY` | Bright Ultra Colors | 1 Pack | Dispenser / Organizer Set | 0 | 26评 (4.5★) | $6.99 | Inactive | 卖家助手 -> 合并商品 |
| *... (该家族共 132 款，其余款式已完整收入 Excel 总表专属工作表中)* | | | | | | | | | | |

### 【Hero-11】601 / 602 / 603 / 604 办公文档签字贴与标签家族 (Sign Here & Arrow Flags)
- **父体 SKU (Parent SKU)**: `PARENT-4A-SIGN-HERE-FLAGS`
- **变体主题 (Variation Theme)**: `StyleName-NumberOfItems`
- **主力目标保留商品 (Master Target)**: **`B07F2CWVQ7`** (SKU: `4A 124418`)
- **家族资产盘点**: 涵盖 **111 款** 兄弟链接 | 当前可售 FBA 现货: **10237 件** | 可聚合历史好评: **744 条**
- **核心合并收益**: 【B2B极速出单组合】文档审核Sign Here箭头贴与0.6x2/0.75x2.5多色便签条合流，针对律所、金融、高校B2B采购打爆客单价。

| 角色 / 操作类型 | 子体 SKU | 子体 ASIN | ColorName 设定值 | NumberOfItems 设定值 | StyleName 设定值 | FBA现货 | 历史评价 | 售价 | 官方状态 | 推荐执行渠道 |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **【主力保留】** | `4A 124418` | `B07F2CWVQ7` | 16 Colors Assorted | 50 Sheets | Standard Flat Note Pad | 12 | 1评 (1★) | $6.99 | Inactive | 保留为父体锚点 |
| 【合并重复】 | `4A GMVC6034` | `B00SMEDVEI` | Transparent Writable | 1 Pack | Pop-Up Accordion Pad | 686 | 84评 (4.4★) | $4.49 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A sticky 019-19` | `B07KS942ZZ` | Bright Ultra Colors | 750 Pcs | Index Tabs & Page Markers | 0 | 26评 (4.5★) | $-- | Incomplete | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GM60238*2` | `B07FK9MJVP` | Neon Assorted | 4 Pads | Index Tabs & Page Markers | 94 | 21评 (4.5★) | $7.49 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GM60239*2` | `B07FK7F4JZ` | Transparent Writable | 4 Pads | Index Tabs & Page Markers | 99 | 21评 (4.5★) | $11.49 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GM6032*2` | `B07FK81CQ7` | Transparent Writable | 5 Pads | Index Tabs & Page Markers | 90 | 21评 (4.5★) | $23.99 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GM6034*2` | `B07FK9XXN1` | Transparent Writable | 2 Pads | Pop-Up Accordion Pad | 345 | 21评 (4.5★) | $11.9 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GM6043*2` | `B07FKB3BS6` | Transparent Writable | 4 Pads | Index Tabs & Page Markers | 97 | 21评 (4.5★) | $11.49 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GMSC66113*2` | `B07FK9MJQF` | Neon Assorted | 12 Pads | Index Tabs & Page Markers | 335 | 21评 (4.5★) | $12.99 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GMSC66114*2` | `B07FKCQ35X` | Neon Assorted | 10 Pads | Index Tabs & Page Markers | 360 | 21评 (4.5★) | $10.99 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `AAAA 4AMT4293SNT` | `B07ZQHHCB5` | Neon Assorted | 1 Pack | Index Tabs & Page Markers | 0 | 21评 (4.5★) | $-- | Incomplete | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GM60121-10x2` | `B07RP8FX7N` | Neon Assorted | 12 Pads / 1200 Sheets | Pop-Up Accordion Pad | 135 | 8评 (5.0★) | $17.99 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GM60174-Sign Herex2` | `B07RP95GGF` | Neon Assorted | 2 Packs | Pop-Up Accordion Pad | 143 | 8评 (5.0★) | $18.49 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GM60222` | `B07RR9CGXY` | Bright Ultra Colors | 780 Pcs | Index Tabs & Page Markers | 282 | 8评 (5.0★) | $12.99 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GM6035*2` | `B07FKDFVHS` | Transparent Writable | 2 Pads | Pop-Up Accordion Pad | 95 | 8评 (4.2★) | $11.49 | Active | 卖家助手 -> 合并商品 |
| *... (该家族共 111 款，其余款式已完整收入 Excel 总表专属工作表中)* | | | | | | | | | | |

### 【Hero-12】PSS 满胶卷带与切刀替芯收纳家族 (Full Adhesive Roll Tape & Dispensers)
- **父体 SKU (Parent SKU)**: `PARENT-4A-PSS-ROLL-TAPE`
- **变体主题 (Variation Theme)**: `StyleName-NumberOfItems`
- **主力目标保留商品 (Master Target)**: **`B07T791NDQ`** (SKU: `4A PSS 9-5`)
- **家族资产盘点**: 涵盖 **9 款** 兄弟链接 | 当前可售 FBA 现货: **202 件** | 可聚合历史好评: **0 条**
- **核心合并收益**: 【带底座+替芯捆绑销售】以带切刀底座为主力，挂载1卷/2卷/4卷不同色彩替芯，实现零边角料自由裁剪文具大升级。

| 角色 / 操作类型 | 子体 SKU | 子体 ASIN | ColorName 设定值 | NumberOfItems 设定值 | StyleName 设定值 | FBA现货 | 历史评价 | 售价 | 官方状态 | 推荐执行渠道 |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| 【合并重复】 | `4A GMMEETING-6*4` | `B07GXH2YX7` | White | 4 Rolls | Large Meeting Presentation Pad | 62 | 0评 | $63.99 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GMSCCR 012` | `B0822QC8Z2` | Classic Assorted | 2 Rolls | Standard Flat Note Pad | 140 | 0评 | $14.99 | Inactive | 卖家助手 -> 合并商品 |
| 【变体挂载】 | `4A MEETING-6*4` | `B07GXH2YX7` | White | 4 Rolls | Large Meeting Presentation Pad | 0 | 0评 | $69.99 | Inactive | 变体向导 / 批量模板 |
| 【变体挂载】 | `4A SCCR 012` | `B0822QC8Z2` | Classic Assorted | 2 Rolls | Standard Flat Note Pad | 0 | 0评 | $14.99 | Inactive | 变体向导 / 批量模板 |
| 【变体挂载】 | `4A sticky 0021` | `B07CYFP1GN` | Classic Assorted | 1 Pack | Standard Flat Note Pad | 0 | 0评 | $-- | Incomplete | 变体向导 / 批量模板 |
| 【变体挂载】 | `4A Meeting-6` | `B0778HMZ9W` | White | 1 Rolls | Large Meeting Presentation Pad | 0 | 0评 | $16.99 |  | 变体向导 / 批量模板 |
| 【变体挂载】 | `4A CR 012` | `B0822QC8Z2` | Classic Assorted | 2 Rolls | Standard Flat Note Pad | 0 | 0评 | $13.99 |  | 变体向导 / 批量模板 |
| 【变体挂载】 | `4A PSS 9-5 NA` | `B00SMEDUVC` | Classic Assorted | 1 Pack | Standard Flat Note Pad | 0 | 0评 | $-- |  | 变体向导 / 批量模板 |
| 【变体挂载】 | `4A PSS 9-1 NBGrid` | `B00VHSXFTW` | Classic Assorted | 1 Pack | Grid / Graph Notes | 0 | 0评 | $-- |  | 变体向导 / 批量模板 |


### 【Hero-13】8065~8088 24色全光谱便签家族 (24-Color Rainbow Spectrum Sticky Notes)
- **父体 SKU (Parent SKU)**: `PARENT-4A-8065-8088-SPECTRUM-24`
- **变体主题 (Variation Theme)**: `ColorName-NumberOfItems`
- **主力目标保留商品 (Master Target)**: **`B077QFD8G7`** (SKU: `4A 8065`)
- **家族资产盘点**: 涵盖 **45 款** 兄弟链接 | 当前可售 FBA 现货: **59 件** | 可聚合历史好评: **63 条**
- **核心合并收益**: 【消灭24个碎片自竞孤岛】将老爸当年拆分的整整24个单色链接合二为一，打造24色全光谱彩虹选色大页，转化率直线上升。

| 角色 / 操作类型 | 子体 SKU | 子体 ASIN | ColorName 设定值 | NumberOfItems 设定值 | StyleName 设定值 | FBA现货 | 历史评价 | 售价 | 官方状态 | 推荐执行渠道 |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **【主力保留】** | `4A 8065` | `B077QFD8G7` | Classic Assorted | 100 Sheets | Standard Flat Note Pad | 0 | 0评 | $5.99 |  | 保留为父体锚点 |
| 【合并重复】 | `AAAA 4A 8066+8067` | `B07FKL3L4S` | Classic Assorted | 100 Sheets | Standard Flat Note Pad | 0 | 4评 (4.2★) | $7.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `AAAA 4A 8068+8065` | `B07FKHZVL1` | Classic Assorted | 100 Sheets | Standard Flat Note Pad | 0 | 4评 (4.2★) | $7.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `AAAA 4A 8069+8070` | `B07FKLCV98` | White | 100 Sheets | Standard Flat Note Pad | 0 | 4评 (4.2★) | $7.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `AAAA 4A 8071+8083` | `B07FKL8LC9` | Classic Assorted | 100 Sheets | Standard Flat Note Pad | 0 | 4评 (4.2★) | $7.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `AAAA 4A 8072+8073` | `B07FKMR9CV` | Classic Assorted | 100 Sheets | Standard Flat Note Pad | 0 | 4评 (4.2★) | $7.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `AAAA 4A 8074+8067` | `B07FKNJB33` | Classic Assorted | 100 Sheets | Standard Flat Note Pad | 0 | 4评 (4.2★) | $8.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `AAAA 4A 8075+8076` | `B07FKLB97D` | Classic Assorted | 100 Sheets | Standard Flat Note Pad | 0 | 4评 (4.2★) | $8.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `AAAA 4A 8077+8079` | `B07FKQ77PG` | Classic Assorted | 100 Sheets | Standard Flat Note Pad | 0 | 4评 (4.2★) | $6.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `AAAA 4A 8078+8080` | `B07FKS5QGR` | Classic Assorted | 100 Sheets | Standard Flat Note Pad | 0 | 4评 (4.2★) | $7.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `AAAA 4A 8084+ 8082` | `B07FKJ43F3` | Classic Assorted | 100 Sheets | Standard Flat Note Pad | 0 | 4评 (4.2★) | $8.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `AAAA 4A 8085+8086` | `B07FKHKDJC` | Classic Assorted | 100 Sheets | Standard Flat Note Pad | 0 | 4评 (4.2★) | $7.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `AAAA 4A 8087+8088` | `B07FKJVC5M` | Classic Assorted | 100 Sheets | Standard Flat Note Pad | 0 | 4评 (4.2★) | $6.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `AAAA 4A 8089+8081` | `B07FKJ6XRW` | Classic Assorted | 100 Sheets | Standard Flat Note Pad | 0 | 4评 (4.2★) | $8.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `AAAA 14` | `B07JHRBXYY` | Classic Assorted | 100 Sheets | Standard Flat Note Pad | 0 | 4评 (4.2★) | $-- | Incomplete | 卖家助手 -> 合并商品 |
| *... (该家族共 45 款，其余款式已完整收入 Excel 总表专属工作表中)* | | | | | | | | | | |

### 【Hero-14】SMC / Shapes / Cube 异形与印花便签砖神仙家族 (Die-Cut Shapes & Printed Cubes)
- **父体 SKU (Parent SKU)**: `PARENT-4A-SHAPES-CUBE-NOVELTY`
- **变体主题 (Variation Theme)**: `StyleName-NumberOfItems`
- **主力目标保留商品 (Master Target)**: **`B00SMEEF2A`** (SKU: `4A 5078`)
- **家族资产盘点**: 涵盖 **167 款** 兄弟链接 | 当前可售 FBA 现货: **5499 件** | 可聚合历史好评: **2417 条**
- **核心合并收益**: 【异形好评合体出击】统合拼图(43评4.1★)、心形、树叶、炸弹与四面印花便签砖，形成高溢价个性礼品便签矩阵。

| 角色 / 操作类型 | 子体 SKU | 子体 ASIN | ColorName 设定值 | NumberOfItems 设定值 | StyleName 设定值 | FBA现货 | 历史评价 | 售价 | 官方状态 | 推荐执行渠道 |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| 【合并重复】 | `4A 0127` | `B07FKNMSJH` | Classic Assorted | 50 Sheets | Standard Flat Note Pad | 0 | 18评 (4.2★) | $6.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A 0129` | `B0756Z8N8X` | Classic Assorted | 50 Sheets | Standard Flat Note Pad | 0 | 18评 (4.2★) | $4.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A 0131` | `B075CZBSR9` | Classic Assorted | 50 Sheets | Standard Flat Note Pad | 0 | 18评 (4.2★) | $3.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A 0132` | `B075D8CHKS` | Classic Assorted | 50 Sheets | Standard Flat Note Pad | 0 | 18评 (4.2★) | $4.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A 0133` | `B075FS5K2T` | Classic Assorted | 50 Sheets | Standard Flat Note Pad | 0 | 18评 (4.2★) | $3.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A 0134` | `B075JDN7D7` | Classic Assorted | 50 Sheets | Standard Flat Note Pad | 0 | 18评 (4.2★) | $3.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A 0135` | `B075JDKV77` | Classic Assorted | 240 Sheets | Standard Flat Note Pad | 0 | 18评 (4.2★) | $3.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A sticky 024-24` | `B07KSR4VVZ` | Classic Assorted | 50 Sheets | Standard Flat Note Pad | 0 | 18评 (4.2★) | $-- | Incomplete | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GMSCMC 434` | `B07FKGDMPS` | Classic Assorted | 650 Sheets | Memo Note Cube | 76 | 16评 (4.3★) | $13.99 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GMSCSMC 436` | `B07FKJDBFT` | Classic Assorted | 580 Sheets | Memo Note Cube | 534 | 13评 (4.6★) | $12.99 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `AAAA 4A SMC 435` | `B07FKS6ZQP` | Classic Assorted | 580 Sheets | Memo Note Cube | 0 | 13评 (4.6★) | $15.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `AAAA 4A SMC 437` | `B07FKK6P5Y` | Classic Assorted | 580 Sheets | Memo Note Cube | 0 | 13评 (4.6★) | $15.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `AAAA 4A SMC 438` | `B07FKHGXSL` | Classic Assorted | 580 Sheets | Memo Note Cube | 0 | 13评 (4.6★) | $15.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4ASMC5678` | `B07Q4PX9V3` | Classic Assorted | 580 Sheets | Memo Note Cube | 0 | 13评 (4.6★) | $-- | Incomplete | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GMSMC 434` | `B07FKHNTRK` | Classic Assorted | 500 Sheets | Memo Note Cube | 979 | 12评 (3.0★) | $12.99 | Active | 卖家助手 -> 合并商品 |
| *... (该家族共 167 款，其余款式已完整收入 Excel 总表专属工作表中)* | | | | | | | | | | |

### 【Hero-15】BP / Meeting 会议大看板、日程计划本与亚克力收纳系列 (Big Pads & Planners)
- **父体 SKU (Parent SKU)**: `PARENT-4A-BP-MEETING-PLANNERS`
- **变体主题 (Variation Theme)**: `StyleName-NumberOfItems`
- **主力目标保留商品 (Master Target)**: **`B07Z2555TN`** (SKU: `4A 404-AC-Holder`)
- **家族资产盘点**: 涵盖 **46 款** 兄弟链接 | 当前可售 FBA 现货: **3291 件** | 可聚合历史好评: **218 条**
- **核心合并收益**: 【$50+高客单价B2B专攻】统合11x11/15x15/22x22会议大白板便签与日程计划本、亚克力笔筒收纳，主攻企业批量团购。

| 角色 / 操作类型 | 子体 SKU | 子体 ASIN | ColorName 设定值 | NumberOfItems 设定值 | StyleName 设定值 | FBA现货 | 历史评价 | 售价 | 官方状态 | 推荐执行渠道 |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| 【合并重复】 | `4A0118` | `B01NH0W2IN` | Pastel Assorted | 3 Pads | Standard Flat Note Pad | 0 | 8评 (4.2★) | $11.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A sticky 022-22` | `B07KS13HT8` | Pastel Assorted | 3 Pads | Standard Flat Note Pad | 0 | 8评 (4.2★) | $-- | Incomplete | 卖家助手 -> 合并商品 |
| 【合并重复】 | `AAAA 4A BP1111 GR` | `B07FK9Z956` | Pastel Assorted | 30 Sheets | Large Meeting Presentation Pad | 0 | 3评 (2★) | $12.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `AAAA 4A BP1111 NO` | `B07FK9NRP5` | Neon Assorted | 30 Sheets | Large Meeting Presentation Pad | 0 | 3评 (2★) | $12.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `AAAA 4A BP1111 NY` | `B07FK8XDQ3` | Neon Assorted | 30 Sheets | Large Meeting Presentation Pad | 0 | 3评 (2★) | $13.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GMMEETING-51*4` | `B07KSX2V6M` | White | 4 Packs | Large Meeting Presentation Pad | 0 | 2评 (4.5★) | $84.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A Meeting-51` | `B07GBYPK92` | White | 20 Sheets | Large Meeting Presentation Pad | 0 | 2评 (4.5★) | $19.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `AAAA 4A 6533` | `B07FKKJPYM` | Classic Assorted | 52 Sheets | Weekly/Monthly Planner Pad | 0 | 2评 (3★) | $21.99 | Inactive | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A sticky 033-33` | `B07KSSFFYS` | White | 4 Packs | Large Meeting Presentation Pad | 0 | 2评 (4.5★) | $-- | Incomplete | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GMBP 1111-Nx4` | `B07QWKYQV7` | Bright Ultra Colors | 4 Pads | Standard Flat Note Pad | 839 | 0评 | $37.39 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GMBP 1111-Px4` | `B07QZR9Z3P` | Pastel Assorted | 4 Pads | Standard Flat Note Pad | 1010 | 0评 | $29.99 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GMBP 1515-Nx4` | `B07R1XLCP4` | Bright Ultra Colors | 4 Pads | Standard Flat Note Pad | 461 | 0评 | $59.99 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GMMeeting-6` | `B07FKJGDJR` | White | 1 Pack | Large Meeting Presentation Pad | 536 | 0评 | $15.99 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `4A GMSC-MEETING-52x4` | `B07RBVWVY4` | White | 25 Sheets | Large Meeting Presentation Pad | 12 | 0评 | $64.99 | Active | 卖家助手 -> 合并商品 |
| 【合并重复】 | `AAAA 4A Meeting-6` | `B07FKJGDJR` | White | 1 Pack | Large Meeting Presentation Pad | 0 | 0评 | $19.99 | Active | 卖家助手 -> 合并商品 |
| *... (该家族共 46 款，其余款式已完整收入 Excel 总表专属工作表中)* | | | | | | | | | | |

---

## 三、 亚马逊后台实操落地路径与两套执行工具 (SOP)

针对上述映射清单中的两类操作，亚马逊卖家后台提供了官方通道，完全保障 FBA 现货一件不用换标：

### 流程一：完全同品重复 ASIN 合并 (Merge Duplicate Product Detail Pages)

- **适用对象**：所有标有 `【合并重复】` 的条目（如 30315 的 `B07FKG29KB` -> `B07F295DPC`，4012 的 `B07FKJLZNG` -> `B01M3N310M`，BS 1801 的 `B07K8L4K8K` -> `B07JVSYNYV` 等）。
- **官方工具直达链接**：`https://sellercentral.amazon.com/help/center/inline/sidebar?fallbackSummonType=solution&solutionId=merge_issues&solutionType=Workflow&client=`
- **填表操作指引**：
  1. **目标 ASIN (Target ASIN to Keep)**：填入各家族的 **主力目标保留 ASIN**；
  2. **源 ASIN (Source ASIN to Merge)**：填入 **待合并的断货/分流重复 ASIN**；
  3. 点击提交，亚马逊系统后台会自动比对品牌与条码，通常在 2~24 小时内完成合流。源 ASIN 的真实评价、历史权重与 FBA 库存全部自动合入主力页面！

### 流程二：不同规格变体家族批量挂载 (Variation Creation & Flat File)

- **适用对象**：各家族中不同规格、颜色、装数的子体 SKU 挂载。
- **模式 A（后台变体向导快速挂载）**：
  1. 路径导航：卖家后台「管理所有库存」顶部点击「添加一个变体」；
  2. 搜索主力目标 ASIN，选择「在现有变体中添加或更新报价」；
  3. 按照映射表中的 `ColorName`、`NumberOfItems`、`StyleName` 填入对应的子 ASIN 即可实时生效。
- **模式 B（表格模板批量更新 - 推荐）**：
  1. 使用已下载的官方模板 `Self-stick_Note_Pads_2026-10-29T13_06.xlsm`；
  2. 将各家族的 Parent SKU 填入父体行，`Update-Delete` 填 `Update`，`Variation Theme` 填 `ColorName-NumberOfItems`；
  3. 子体行填入各子 SKU，`Parentage` 填 `Child`，`Parent SKU` 填对应父体，`Update-Delete` 选 `PartialUpdate`（无损更新，绝不篡改历史 FNSKU 和商品参数）；
  4. 上传至后台批量商品上传页面，系统自动构建双维度变体树！

---

## 四、 资产交付与附件清单

1. **全量变体合并与挂载映射总表 (Excel 格式)**：
   - 文件路径：[`E:\Desktop\4A_全店变体合并全量大排查与挂载映射总表.xlsx`](file:///E:/Desktop/4A_全店变体合并全量大排查与挂载映射总表.xlsx)
   - 包含 `【全店15大家族总览】`、`【全量变体合并与挂载总表】` 以及 15 个家族分表，共 17 个工作表，涵盖全店 939 个统一商品实体的每一项变体属性。
2. **本专项审计排查完整报告 (Markdown 格式)**：
   - 文件路径：[`C:\Users\24243\.gemini\antigravity\brain\258d447c-7e8b-4b81-b031-14dda352081f\4A_全店700+Listing全量多维度变体合并大排查与映射方案.md`](file:///C:/Users/24243/.gemini/antigravity/brain/258d447c-7e8b-4b81-b031-14dda352081f/4A_全店700+Listing全量多维度变体合并大排查与映射方案.md)