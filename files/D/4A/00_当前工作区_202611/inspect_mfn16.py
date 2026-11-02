import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r"D:\4A\00_当前工作区_202611\residual_mfn16_evidence_audit.json", "r", encoding="utf-8") as f:
    mfn16 = json.load(f)

print(f"Total items in residual_mfn16: {len(mfn16)}")
for item in mfn16:
    sku = item.get('sku')
    cls = item.get('audit_classification')
    conf_fields = item.get('conflicting_fields')
    cat_val = item.get('amazon_catalog_conflicting_value')
    merch_val = item.get('merchant_conflicting_value')
    mfn_qty = item.get('exact_mfn_declared_quantity')
    print(f"SKU: {sku:18} | Class: {cls:25} | Fields: {conf_fields} | Cat: {cat_val!r:25} | Merch: {merch_val!r:20} | Qty: {mfn_qty}")
