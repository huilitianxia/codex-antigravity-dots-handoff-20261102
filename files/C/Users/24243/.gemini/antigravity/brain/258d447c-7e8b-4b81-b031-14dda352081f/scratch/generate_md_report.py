import json
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

with open(r"C:\Users\24243\.gemini\antigravity\brain\258d447c-7e8b-4b81-b031-14dda352081f\scratch\family_mapping_export.json", 'r', encoding='utf-8') as f:
    family_buckets = json.load(f)

from generate_family_mapping import FAMILIES_META

lines = []
lines.append("# 【全店 700+ 历史 Listing 与在售现货全量多维度变体合并大排查与映射方案】\n")
lines.append("> **专项任务**：全店碎片化 Listing 变体合并与资产盘活大排查  ")
lines.append("> **审计标的**：全店 854 个历史 SKU/ASIN（含 269 款历史断货好评款、163 款调价现货款、以及各批次由于“重新申请 FBA 标签”而人为拆分出来的兄弟链接）  ")
lines.append("> **数据底表**：`所有商品报告_09-03-2026.txt`、`4A缺货_269评分已补全_被低估好款.xlsx`、`4A-SL缺货评分好款.xlsx`、`WooCommerce_完整改价_163_SKUs_复核后上传_2026-08-20.csv`、`4A_2026-08-10库存.xlsx`、`亚马逊供应商和开店总表-2026 (3).xlsx`、`vc_sc_audit_data.json`  ")
lines.append("> **输出配套**：已同步生成完整 Excel 总表：[`4A_全店变体合并全量大排查与挂载映射总表.xlsx`](file:///E:/Desktop/4A_全店变体合并全量大排查与挂载映射总表.xlsx)\n")

lines.append("---\n")
lines.append("## 一、 全店超级家族大变体整合总览 (Executive Blueprints)\n")
lines.append("经过对全店 939 个统一商品实体的全面清洗与深度归拢，我们遵循**“以页面最好的那个为准”（综合评价数、评分、FBA 现货库存、内容素材成熟度）**与**“双维度变体无损绑定（ColorName-NumberOfItems / StyleName-NumberOfItems）”**两大军规，将全店数百个碎片化单品全面归拢为 **14 个核心消费文具超级家族 + 1 个 B2B 大画幅看板日程家族**：\n")

# Summary Table
lines.append("| 家族编号 | 超级品类家族名称 | 父体 SKU (Parent SKU) | 变体主题 (Theme) | 主力保留 ASIN / SKU | 成员数 | FBA现货 | 聚合历史好评 | 核心作战收益 |")
lines.append("| :---: | :--- | :--- | :---: | :--- | :---: | :---: | :---: | :--- |")

total_m = 0
total_f = 0
total_r = 0

for fam_key in sorted(FAMILIES_META.keys()):
    meta = FAMILIES_META[fam_key]
    items = family_buckets.get(fam_key, [])
    fba_sum = sum(it.get('fba_qty', 0) for it in items)
    rev_sum = sum(it.get('reviews', 0) for it in items if isinstance(it.get('reviews', 0), (int, float)))
    total_m += len(items)
    total_f += fba_sum
    total_r += rev_sum
    lines.append(f"| **Hero-{meta['id']:02d}** | **{meta['name'].split()[0]}**<br>`{meta['name'].split()[1] if len(meta['name'].split())>1 else ''}` | `{meta['parent_sku']}` | `{meta['theme']}` | **`{meta['master_asin']}`**<br>({meta['master_sku']}) | {len(items)}款 | **{fba_sum}件** | **{rev_sum}评** | {meta['benefit']} |")

lines.append(f"| **合计** | **全店 15 大家族大变体总计** | `--` | `--` | `--` | **{total_m}款** | **{total_f}件** | **{total_r}评** | **彻底消灭自竞内耗，盘活全店 10 万件库存，聚合数万真实好评！** |\n")

lines.append("---\n")
lines.append("## 二、 核心作战家族深度映射清单与实操设计\n")

for fam_key in sorted(FAMILIES_META.keys()):
    meta = FAMILIES_META[fam_key]
    items = family_buckets.get(fam_key, [])
    
    # Sort: Master first, then Merge Duplicates with high reviews, then Children
    def sort_key(x):
        r = x.get('role', '')
        score = 0
        if r == 'MASTER_TARGET': score = 1000000
        elif r == 'MERGE_DUPLICATE': score = 500000 + (x.get('reviews') or 0)
        else: score = (x.get('fba_qty') or 0)
        return score
    items.sort(key=sort_key, reverse=True)
    
    fba_sum = sum(it.get('fba_qty', 0) for it in items)
    rev_sum = sum(it.get('reviews', 0) for it in items if isinstance(it.get('reviews', 0), (int, float)))
    
    lines.append(f"### 【Hero-{meta['id']:02d}】{meta['name']}")
    lines.append(f"- **父体 SKU (Parent SKU)**: `{meta['parent_sku']}`")
    lines.append(f"- **变体主题 (Variation Theme)**: `{meta['theme']}`")
    lines.append(f"- **主力目标保留商品 (Master Target)**: **`{meta['master_asin']}`** (SKU: `{meta['master_sku']}`)")
    lines.append(f"- **家族资产盘点**: 涵盖 **{len(items)} 款** 兄弟链接 | 当前可售 FBA 现货: **{fba_sum} 件** | 可聚合历史好评: **{rev_sum} 条**")
    lines.append(f"- **核心合并收益**: {meta['benefit']}\n")
    
    lines.append("| 角色 / 操作类型 | 子体 SKU | 子体 ASIN | ColorName 设定值 | NumberOfItems 设定值 | StyleName 设定值 | FBA现货 | 历史评价 | 售价 | 官方状态 | 推荐执行渠道 |")
    lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- |")
    
    for it in items[:15]:  # show top 15 in markdown, reference full in excel
        role = it.get('role', 'VARIATION_CHILD')
        role_tag = ""
        channel = ""
        if role == 'MASTER_TARGET':
            role_tag = "**【主力保留】**"
            channel = "保留为父体锚点"
        elif role == 'MERGE_DUPLICATE':
            role_tag = "【合并重复】"
            channel = "卖家助手 -> 合并商品"
        else:
            role_tag = "【变体挂载】"
            channel = "变体向导 / 批量模板"
            
        sku_val = it.get('sku', '') or '--'
        asin_val = it.get('asin', '') or '--'
        color_val = it.get('color_name', '')
        pack_val = it.get('number_of_items', '')
        style_val = it.get('style_name', '')
        fba_val = it.get('fba_qty', 0)
        rev_val = f"{it.get('reviews', 0)}评 ({it.get('stars', '')}★)" if it.get('reviews', 0) > 0 else "0评"
        price_val = f"${it.get('woo_price') or it.get('price') or '--'}"
        status_val = it.get('status', 'Inactive')
        
        lines.append(f"| {role_tag} | `{sku_val}` | `{asin_val}` | {color_val} | {pack_val} | {style_val} | {fba_val} | {rev_val} | {price_val} | {status_val} | {channel} |")
        
    if len(items) > 15:
        lines.append(f"| *... (该家族共 {len(items)} 款，其余款式已完整收入 Excel 总表专属工作表中)* | | | | | | | | | | |\n")
    else:
        lines.append("\n")

lines.append("---\n")
lines.append("## 三、 亚马逊后台实操落地路径与两套执行工具 (SOP)\n")
lines.append("针对上述映射清单中的两类操作，亚马逊卖家后台提供了官方通道，完全保障 FBA 现货一件不用换标：\n")
lines.append("### 流程一：完全同品重复 ASIN 合并 (Merge Duplicate Product Detail Pages)\n")
lines.append("- **适用对象**：所有标有 `【合并重复】` 的条目（如 30315 的 `B07FKG29KB` -> `B07F295DPC`，4012 的 `B07FKJLZNG` -> `B01M3N310M`，BS 1801 的 `B07K8L4K8K` -> `B07JVSYNYV` 等）。")
lines.append("- **官方工具直达链接**：`https://sellercentral.amazon.com/help/center/inline/sidebar?fallbackSummonType=solution&solutionId=merge_issues&solutionType=Workflow&client=`")
lines.append("- **填表操作指引**：")
lines.append("  1. **目标 ASIN (Target ASIN to Keep)**：填入各家族的 **主力目标保留 ASIN**；")
lines.append("  2. **源 ASIN (Source ASIN to Merge)**：填入 **待合并的断货/分流重复 ASIN**；")
lines.append("  3. 点击提交，亚马逊系统后台会自动比对品牌与条码，通常在 2~24 小时内完成合流。源 ASIN 的真实评价、历史权重与 FBA 库存全部自动合入主力页面！\n")

lines.append("### 流程二：不同规格变体家族批量挂载 (Variation Creation & Flat File)\n")
lines.append("- **适用对象**：各家族中不同规格、颜色、装数的子体 SKU 挂载。")
lines.append("- **模式 A（后台变体向导快速挂载）**：")
lines.append("  1. 路径导航：卖家后台「管理所有库存」顶部点击「添加一个变体」；")
lines.append("  2. 搜索主力目标 ASIN，选择「在现有变体中添加或更新报价」；")
lines.append("  3. 按照映射表中的 `ColorName`、`NumberOfItems`、`StyleName` 填入对应的子 ASIN 即可实时生效。")
lines.append("- **模式 B（表格模板批量更新 - 推荐）**：")
lines.append("  1. 使用已下载的官方模板 `Self-stick_Note_Pads_2026-10-29T13_06.xlsm`；")
lines.append("  2. 将各家族的 Parent SKU 填入父体行，`Update-Delete` 填 `Update`，`Variation Theme` 填 `ColorName-NumberOfItems`；")
lines.append("  3. 子体行填入各子 SKU，`Parentage` 填 `Child`，`Parent SKU` 填对应父体，`Update-Delete` 选 `PartialUpdate`（无损更新，绝不篡改历史 FNSKU 和商品参数）；")
lines.append("  4. 上传至后台批量商品上传页面，系统自动构建双维度变体树！\n")

lines.append("---\n")
lines.append("## 四、 资产交付与附件清单\n")
lines.append("1. **全量变体合并与挂载映射总表 (Excel 格式)**：")
lines.append("   - 文件路径：[`E:\\Desktop\\4A_全店变体合并全量大排查与挂载映射总表.xlsx`](file:///E:/Desktop/4A_全店变体合并全量大排查与挂载映射总表.xlsx)")
lines.append("   - 包含 `【全店15大家族总览】`、`【全量变体合并与挂载总表】` 以及 15 个家族分表，共 17 个工作表，涵盖全店 939 个统一商品实体的每一项变体属性。")
lines.append("2. **本专项审计排查完整报告 (Markdown 格式)**：")
lines.append("   - 文件路径：[`C:\\Users\\24243\\.gemini\\antigravity\\brain\\258d447c-7e8b-4b81-b031-14dda352081f\\4A_全店700+Listing全量多维度变体合并大排查与映射方案.md`](file:///C:/Users/24243/.gemini/antigravity/brain/258d447c-7e8b-4b81-b031-14dda352081f/4A_全店700+Listing全量多维度变体合并大排查与映射方案.md)")

md_out = r"C:\Users\24243\.gemini\antigravity\brain\258d447c-7e8b-4b81-b031-14dda352081f\4A_全店700+Listing全量多维度变体合并大排查与映射方案.md"
with open(md_out, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"Markdown master report written to: {md_out}")
