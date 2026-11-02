import json

json_path = r'D:\4A\00_当前工作区_202611\residual_mfn16_evidence_audit.json'
with open(json_path, 'r', encoding='utf-8') as f:
    audit_data = json.load(f)

md_lines = []
md_lines.append("# 4A 亚马逊运营：Residual MFN 16 SKU 实物证据核验与目录冲突审计报告")
md_lines.append("")
md_lines.append("> **生成时间**：2026-11-01 20:18 CST  ")
md_lines.append("> **执行架构**：Argon 主脑下属 3.8 Evidence Worker  ")
md_lines.append("> **证据范围**：`residual62-closeout.json` 中 `inventory_group == '仅MFN有申报库存'` 的全部 16 行商品  ")
md_lines.append("> **执行铁律遵循**：严格只读，无任何线上修改或文件覆盖；属性比对 100% 依托实物包装图、官方总表与官方报告快照。")
md_lines.append("")
md_lines.append("---")
md_lines.append("")
md_lines.append("## 一、总体审计结论与分类统计")
md_lines.append("")
md_lines.append("16 个 MFN 有申报库存行中：")
md_lines.append("- **SAFE_CATALOG_MATCH_PROVEN（实物证据证明目录正确，卖家现值为盲目覆盖）**：**13 行**（累计 MFN 库存 2,569 套）")
md_lines.append("- **APPEAL_CATALOG_WRONG（实物/总表证明卖家属性正确，目录属性被污染）**：**2 行**（`4A 186`, `4A 187`；前台 Inactive，目录将件数/尺寸拼入 Color 字段，需工单申诉修正）")
md_lines.append("- **DEFERRED_FAMILY_OR_BLOCKED（非 8541 冲突 / 家族架构阻断待修）**：**1 行**（`4A GM40624*2`；报错码为 99022，缺少 Color Map / `standardized_values`，暂无目录冲突值）")
md_lines.append("")
md_lines.append("### 16 行总览核验表")
md_lines.append("")
md_lines.append("| 序号 | SKU | ASIN | MFN申报库存 | 状态 | 冲突字段 | 卖家提交值 | 亚马逊目录值 | 实物/总表证据分类 |")
md_lines.append("|---|---|---|---|---|---|---|---|---|")

for idx, item in enumerate(audit_data, start=1):
    m_val = str(item['merchant_conflicting_value']).replace('|', '/')
    a_val = str(item['amazon_catalog_conflicting_value']).replace('|', '/')
    conf_fld = ", ".join(item['conflicting_fields'])
    qty_str = str(int(item['exact_mfn_declared_quantity'])) if item['exact_mfn_declared_quantity'] is not None else "-"
    md_lines.append(f"| {idx:02d} | `{item['sku']}` | `{item['asin']}` | {qty_str} | {item['listing_status']} | `{conf_fld}` | {m_val} | {a_val} | **`{item['audit_classification']}`** |")

md_lines.append("")
md_lines.append("---")
md_lines.append("")
md_lines.append("## 二、逐 SKU 详细核验与证据链拆解")
md_lines.append("")

for idx, item in enumerate(audit_data, start=1):
    md_lines.append(f"### {idx:02d}. SKU: `{item['sku']}` (ASIN: `{item['asin']}`)")
    md_lines.append(f"- **审计分类**：**`{item['audit_classification']}`**")
    md_lines.append(f"- **申报库存**：`{item['exact_mfn_declared_quantity']}` | **在售状态**：`{item['listing_status']}`")
    md_lines.append(f"- **冲突字段**：`{item['conflicting_fields']}`")
    md_lines.append(f"- **卖家提交值**：`{item['merchant_conflicting_value']}`")
    md_lines.append(f"- **亚马逊目录值**：`{item['amazon_catalog_conflicting_value']}`")
    md_lines.append(f"- **原始 8541 / 报错信息**：")
    for code, msg in item['error_messages'].items():
        md_lines.append(f"  - `[{code}]`: {msg}")
    md_lines.append(f"- **分类报告快照（10-31 模板第 {item['category_report_snapshot']['template_row_index']} 行）**：")
    md_lines.append(f"  - Title: `{item['category_report_snapshot']['title']}`")
    md_lines.append(f"  - Color: `{item['category_report_snapshot']['color']}` | Color Map: `{item['category_report_snapshot']['color_map']}`")
    md_lines.append(f"  - Manufacturer: `{item['category_report_snapshot']['manufacturer']}` | Model: `{item['category_report_snapshot']['model_number']}`")
    md_lines.append(f"  - Product Type: `{item['category_report_snapshot']['product_type']}` | Parent SKU: `{item['category_report_snapshot']['parent_sku']}`")
    md_lines.append(f"- **总表核验（Sheet: {item['master_sheet_evidence']['sheet']} R{item['master_sheet_evidence']['row_index']}）**：")
    md_lines.append(f"  - 总表 SKU: `{item['master_sheet_evidence']['master_sku']}`")
    md_lines.append(f"  - VC 条码/ASIN: `{item['master_sheet_evidence']['vc_upc']}` / `{item['master_sheet_evidence']['vc_asin']}`")
    md_lines.append(f"  - 店铺 条码/ASIN: `{item['master_sheet_evidence']['sl_upc']}` / `{item['master_sheet_evidence']['sl_asin']}`")
    md_lines.append(f"  - 总表标题: `{item['master_sheet_evidence']['master_title']}`")
    md_lines.append(f"- **实物图与包装核查证据**：")
    md_lines.append(f"  - 对应原图目录: `{item['physical_photo_evidence']['matched_folders'][0]}`")
    md_lines.append(f"  - 核心核验图片: `{item['physical_photo_evidence']['key_packaging_image']}`")
    md_lines.append(f"  - 实物外观/包装观察: {item['physical_photo_evidence']['physical_visual_description']}")
    md_lines.append(f"- **判定依据**：{item['classification_justification']}")
    md_lines.append("")

md_lines.append("---")
md_lines.append("")
md_lines.append("## 三、后续安全处理路径建议（按 Argon 主脑铁律）")
md_lines.append("")
md_lines.append("1. **针对 13 行 SAFE_CATALOG_MATCH_PROVEN**：")
md_lines.append("   - 均具备实物包装、总表及原图强证据支撑；卖家后台当前值系此前 3.8 脚本大表全量盲目填充（如全量刷成 `Classic Assorted` 或误填 `China`）导致的自造冲突。")
md_lines.append("   - **执行原则**：严格执行**最小字段局部更新（Minimal-Cell Partial Update）**。仅包含 SKU、Exact ID（ASIN）、获批修改的目标字段（`color`、`manufacturer` 或 `standard_product_id`），严禁携带价格或变体大表。")
md_lines.append("2. **针对 2 行 APPEAL_CATALOG_WRONG (`4A 186`, `4A 187`)**：")
md_lines.append("   - 亚马逊目录中将尺寸和包装数量拼合在 `color` 字段中（`Extra Colors 4 X 6-3 Pads` / `Extra Colors 4 X 6-5 Pads`），属于典型的属性污染。")
md_lines.append("   - 目前该两款商品在售状态为 `Inactive`（库存无申报），禁止盲抄目录脏数据；应作为非紧急工单申诉项处理，由主脑统筹在适当时机提交带包装条码图的开眼工单。")
md_lines.append("3. **针对 1 行 DEFERRED_FAMILY_OR_BLOCKED (`4A GM40624*2`)**：")
md_lines.append("   - 该 SKU 报错并非 8541 目录冲突，而是 99022 架构校验错误（Color 为 `White` 但漏填了 Color Map `standardized_values`）。")
md_lines.append("   - 修复仅需补齐 Color Map 为 `White`，无需进行目录对齐。")
md_lines.append("")

summary_path = r'D:\4A\00_当前工作区_202611\residual_mfn16_evidence_summary.md'
with open(summary_path, 'w', encoding='utf-8') as f:
    f.write("\n".join(md_lines))

print(f"Summary markdown written to {summary_path}")
