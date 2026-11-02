import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r"D:\4A\00_Codex交接给Gemini_20261101\03_验收与待办证据\coupon-expanded-execution-ledger.json", "r", encoding="utf-8") as f:
    ledger = json.load(f)

c15 = set(ledger.get("final15_running_asins", []))
c5 = set(ledger.get("final5_running_asins", []))
draft15 = set(ledger.get("second15_draft_added", []))

with open(r"D:\4A\00_Codex交接给Gemini_20261101\03_验收与待办证据\coupon-expansion-77-complete-readonly-audit.json", "r", encoding="utf-8") as f:
    c77_raw = json.load(f)
c77_list = c77_raw if isinstance(c77_raw, list) else c77_raw.get("rows", [])
c77_by_sku = {r["sku"]: r for r in c77_list if "sku" in r}
c77_by_asin = {r["asin"]: r for r in c77_list if "asin" in r}

with open(r"D:\4A\00_当前工作区_202611\high_stock_cashflow_plan.json", "r", encoding="utf-8") as f:
    plan = json.load(f)

print("Plan keys:", list(plan.keys()))
for k, v in plan.items():
    if isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
        print(f"\n--- {k} (len={len(v)}) ---")
        for item in v[:30]:
            sku = str(item.get("sku", ""))
            asin = str(item.get("asin", ""))
            qty = item.get("afn_fulfillable_quantity", item.get("available_qty", item.get("qty", item.get("fulfillable_qty"))))
            in_c15 = asin in c15
            in_c5 = asin in c5
            in_draft15 = asin in draft15
            c77_info = c77_by_sku.get(sku) or c77_by_asin.get(asin) or {}
            tiers = c77_info.get("tiers", [])
            b2b = c77_info.get("b2b")
            price = c77_info.get("price", item.get("your_price", item.get("price")))
            sale_vis = c77_info.get("sale_visible")
            print(f"SKU={sku:25} | ASIN={asin:10} | Qty={str(qty):4} | Price={str(price):6} | SaleVis={str(sale_vis):6} | B2B={str(b2b):6} | Tiers={str(tiers):22} | In15%={in_c15} | In5%={in_c5} | Draft15={in_draft15}")
