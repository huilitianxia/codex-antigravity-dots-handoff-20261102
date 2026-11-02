import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r"D:\4A\00_当前工作区_202611\residual_mfn16_evidence_audit.json", "r", encoding="utf-8") as f:
    mfn_data = json.load(f)

fba_skus = {
    "4A 039": 12,
    "4A 040": 5,
    "4A 037": 2,
    "4A 0166": 3,
    "4A095": 2 # sibling FBA 2, MFN 719
}

print("=== FBA SKUs ===")
fba_sum = sum(fba_skus.values())
print("FBA sum:", fba_sum)

print("\n=== MFN SKUs in audit ===")
mfn_13_skus = [
    "4A092", "4A PSS 9-5 NB", "4A 0153", "4A 0154", "4A 0155",
    "4A 0168", "4A 0169", "4A 0171", "4A 40606", "4A 5036",
    "4A 60238", "4A SF-60238", "4A093"
]

mfn_sum = 0
for item in mfn_data:
    sku = item['sku']
    qty = item.get('exact_mfn_declared_quantity') or 0
    if sku in mfn_13_skus:
        print(f"  {sku:18}: {qty}")
        mfn_sum += qty

print("MFN 13 sum:", mfn_sum)

sku_99022 = "4A GM40624*2"
qty_99022 = 747
print(f"99022 SKU {sku_99022}: {qty_99022}")

# Also 4A095 has MFN 719!
qty_095_mfn = 719

total = fba_sum + mfn_sum + qty_99022
print("\nTotal (FBA 24 + MFN 13 (2569) + 99022 (747)):", total)
print(f"Total exactly: {fba_sum} + {mfn_sum} + {qty_99022} = {total}")
