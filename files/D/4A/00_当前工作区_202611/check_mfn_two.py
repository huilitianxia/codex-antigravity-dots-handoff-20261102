import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r"D:\4A\00_当前工作区_202611\residual_mfn16_evidence_audit.json", "r", encoding="utf-8") as f:
    items = json.load(f)

for item in items:
    if item['sku'] in ['4A PSS 9-5 NB', '4A 40606']:
        print(f"=== {item['sku']} ===")
        print("Conflicting fields:", item.get('conflicting_fields'))
        print("Error messages:", item.get('error_messages'))
        print("Merchant conflicting value:", item.get('merchant_conflicting_value'))
        print("Amazon catalog value:", item.get('amazon_catalog_conflicting_value'))
