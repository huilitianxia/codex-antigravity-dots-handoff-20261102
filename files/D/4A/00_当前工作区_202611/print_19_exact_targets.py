import json

with open(r"D:\4A\00_当前工作区_202611\residual_mfn16_evidence_audit.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for item in data:
    print(f"{item['sku']:18} | {item['asin']} | {item['audit_classification']:28} | fields={item['conflicting_fields']} | merchant={item['merchant_conflicting_value']!r} -> catalog={item['amazon_catalog_conflicting_value']!r}")
