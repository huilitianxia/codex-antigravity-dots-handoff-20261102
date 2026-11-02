# 4A 新任务精简迁移包

更新日期：2026-08-28

## 新任务读取规则

本文件是旧长任务的精简交接背景。新任务应先完整读取本文件，再按具体工作需要读取下方列出的源文件；不要重新扫描旧聊天、全部截图、全部 WorkBuddy 目录或临时文件。涉及当前价格、ASIN 权限、竞品和市场需求时，必须实时核验，不能把旧结果当作当前状态。

## 保留范围

### 1. 4A Amazon 既有 ASIN 报价权限

- 4A Limited 曾通过 Vendor Central 向 Amazon 供货，合作于 2024 年底结束。目标是让 4A Seller Central 店铺向历史 VC ASIN 添加真实品牌方报价，不是转移页面所有权、继承评价或要求移除 Amazon 报价。
- Seller Central 判断路径：`Catalog → Add Products`。`Sell this product` 表示可添加报价；`Apply to sell` 表示需申请；按钮缺失或出现明确错误时，保存 ASIN、SKU、时间、完整错误和证据后再开 case。
- 不以 Buy Box、卖家数量或第三方工具状态推断“Amazon 独占”。
- Case 表述应使用：品牌方/制造商希望向既有 ASIN 添加 genuine offer。不要使用“拿回页面”“继承评价”等说法。
- 保留错误 8541 的处理经验：如果输入的 manufacturer 与 Amazon 目录值冲突，应先匹配目录属性；如目录数据本身错误，再凭品牌、包装、UPC/GS1 和历史 VC 记录申请更正。
- ASIN `B01LVTWP7Q` 已能在美国站目录中建立报价。当前出现两个同 ASIN 的 SKU：系统生成的 `K9-OIMV-XL3E`，以及计划使用的 `4A 301x12-N`。补货应针对计划使用且已有 FNSKU 的 `4A 301x12-N`；不要给自动生成的重复 SKU 补货，除非后续重新确认其用途。
- 不保留 Amazon Support 逐句聊天内容和过程截图。

关键文件：

- `PROJECT_MEMORY.md`
- `source_workbooks/4A_跟卖分类整理_2026-08-11.xlsx`
- `source_workbooks/4A_VC可跟卖检测_2026-08-11.xlsx`
- `../outputs/019ff179-ce00-7621-9ae6-13daf0989ce8/4A_Amazon_Existing_ASIN_Offer_Access_Case_Evidence_2026-08-25.xlsx`

### 2. 产品视频最终要求

- 品牌统一使用 4A 皇冠标志，不再使用“翰林纸院”；右上角可常驻 4A 皇冠。
- 画面为 16:9 横版，建议约 35–45 秒；全部字幕使用英文。
- 重点不是静态产品展示，而是真实人手完成：平滑撕下、粘贴、再次撕下并重新粘贴、在便签上顺滑书写。
- 以用户提供的真实素材为主，仿真补拍只能补足衔接或场景，不能替代关键功能动作。
- 4A 30315 等普通款不是整页满胶；胶只在一侧，轻微自然翘边可以接受。不得错误表现为整张满胶。只有明确标注 Full Adhesive 的款式才可按满胶表现。
- 动作和声音必须同步；去除素材中的人声，只保留轻松明快 BGM 和真实、较轻的撕/贴/写声音。产品介绍段 BGM 可稍大，核心动作段降低音量。
- 功能文字使用透明叠加，不要用遮挡画面的厚重底栏。
- 同系列不同颜色应择优展示，并体现书本、电脑、墙面、杯子、纸箱等多场景使用。
- 已找到的早期 25 秒文件仅供参考，不应当作后来 35–45 秒优化版的最终成品：
  - `../outputs/Hanlin_Paper_Sticky_Notes_English_25s.mp4`
  - `../outputs/翰林纸院便利贴_25秒产品视频.mp4`
- 若新任务继续视频制作，应让用户提供或指定其认可的最新成品和原始素材，不要从旧聊天推测最终文件。

### 3. Amazon 与 WooCommerce 定价

- Amazon 主数据：`source_workbooks/亚马逊供应商和开店总表-2026 (1).xlsx`。Sheet1 有 201 条非空 SKU。A 列为 SKU，L 列为标价，M 列为 2026 折后销售价。
- 价格操作必须使用当前 Seller Central 官方 Price & Quantity 或当前品类 Advanced inventory template；先测试 3–5 个 SKU，再批量上传。
- List Price 必须有真实、可验证的参考依据；不以虚高原价制造折扣。促销优先考虑有期限的 Price Discount/Coupon，并设置不突破利润底线的最低价。
- 三个历史反向价格需特别检查：`4A 6031x4`、`4A 301Mx24`、`4A 303M-PNx12`。
- 4AUSA WooCommerce 的 163 个 SKU 批量改价已核验成功：163/163 与上传文件一致，价格不一致 0，网站未返回 0；其中 141 个原价发生变化。
- 4APAPER 尚未执行同批改价，不能把 4AUSA 的结果当作 4APAPER 已完成。
- 不保留中间上传页面、保存窗口和逐步导航截图。

关键文件：

- `PRICING_AND_BULK_UPLOAD.md`
- `../outputs/019ff179-ce00-7621-9ae6-13daf0989ce8/4A_PriceAndQuantity_100_SKUs_2026-08-17.xlsx`
- `../outputs/019ff179-ce00-7621-9ae6-13daf0989ce8/4A_PriceAndQuantity_SC核验版_23_SKUs_2026-08-17.xlsx`
- `../outputs/019ff179-ce00-7621-9ae6-13daf0989ce8/WooCommerce_测试改价_5_SKUs_2026-08-20.csv`
- `../outputs/019ff179-ce00-7621-9ae6-13daf0989ce8/WooCommerce_完整改价_163_SKUs_复核后上传_2026-08-20.csv`
- `../outputs/019ff179-ce00-7621-9ae6-13daf0989ce8/WooCommerce_商品异常清理清单_2026-08-20.xlsx`
- `../outputs/019ff179-ce00-7621-9ae6-13daf0989ce8/4Ausa_163_SKUs_改价实时核对_2026-08-21.xlsx`

### 4. 网站与 WorkBuddy 迁移背景

- 保留 vHorse、4AUSA、4APAPER 的建站和迁移背景。4AUSA 与 4APAPER 后台均为 WordPress/WooCommerce。
- 4AUSA 当前已完成上述 163 SKU 改价核验；4APAPER 是后续待办。
- vHorse/站点迁移的具体网址、账号和服务器信息不得从记忆猜测；需要时只读取本地 WorkBuddy 的“网站迁移”记录或由用户提供当前后台页面。不得在迁移摘要中保存密码或密钥。
- 不因保留网站背景而自动扫描全部 WorkBuddy 文件；只在具体任务需要时定向读取相关目录。

### 5. 视频拍摄墙与品牌标志板

- 实拍墙宽约 1.2 m。
- 常驻品牌板包含 `HIGH QUALITY STICKY NOTES`、4A 皇冠标志和不同颜色便签本示意图；整体要求美观、有序、不过度鲜艳。
- 已采用约 72 × 16 cm 的常驻标志板方案。系列标题计划另做横幅，放在常驻板下方，不必塞进同一块板。
- 保留设计文件：
  - `../output/pdf/4A_常驻品牌标志板_72x16cm_设计稿.pdf`
  - `../output/pdf/4A_视频系列标题_设计评审与新版样张.pdf`

### 6. 新品海外市场研究（当前待办）

- 国内产品：全面贴替换芯/遮蔽答案/改错题整理类便签，淘宝链接：`https://e.tb.cn/h.8PoENhJn0p158wl?tk=mEANT3BsFGj`。
- 下一步需要实时调研美国及其他海外市场是否存在需求、竞品、常用英文搜索词、Amazon 合规标题、包装数量和建议售价。
- 研究时重点区分：full-adhesive correction notes、answer-cover study notes、mistake correction stickers、study masking notes 等潜在定位；不得仅凭中文直译决定标题。
- 市场需求、竞品价格和 Amazon 搜索结果具有时效性，新任务必须联网重新核验。

## 明确不导入

- Amazon Support 逐句聊天及其截图。
- 产品视频的中间版本和反复评审过程。
- Amazon/WooCommerce 中间上传导航和保存窗口截图。
- Codex/电脑排错、C 盘迁移、快捷方式、重启、高温、额度讨论。
- Sora、Runway、视频模型与 DeepSeek/API 接入讨论。
- 已取消的 Slack/Gmail 工作日晨间简报及连接器历史。

## 新任务默认工作方式

- 先给结论，再说明依据。
- Seller Central、WordPress/WooCommerce 和市场价格等可能变化的信息必须实时核验。
- 批量修改前先做小批测试；外部写入、提交 case、正式上传或删除商品前明确确认目标。
- 不扫描未请求的旧文件，不重新导入上述明确排除的内容。
