import openpyxl, os, re, json

f = r"E:/Desktop/亚马逊供应商和开店总表-2026 (1).xlsx"
wb = openpyxl.load_workbook(f, data_only=True)
ws = wb["Sheet1"]

rows = []
for r in range(2, ws.max_row+1):
    sku = ws.cell(row=r, column=1).value
    vc_upc = ws.cell(row=r, column=2).value
    vc_asin = ws.cell(row=r, column=3).value
    sl_upc = ws.cell(row=r, column=4).value
    sl_asin = ws.cell(row=r, column=5).value
    title = ws.cell(row=r, column=7).value
    price = ws.cell(row=r, column=13).value
    if not sku:
        continue
    # normalize asin lists
    def clean_asin(v):
        if not v: return []
        return [a.strip().upper() for a in re.split(r'[\n,/]', str(v)) if re.match(r'^B0[A-Z0-9]{8}$', a.strip())]
    vc_list = clean_asin(vc_asin)
    sl_list = clean_asin(sl_asin)
    # 共用标记：VC-ASIN 出现在 SL-ASIN 列表中
    shared = [a for a in vc_list if a in sl_list]
    rows.append({
        "sku": str(sku).strip(),
        "vc_upc": str(vc_upc).strip() if vc_upc else "",
        "vc_asin": vc_list,
        "sl_upc": str(sl_upc).strip() if sl_upc else "",
        "sl_asin": sl_list,
        "shared_asin": shared,
        "title": str(title).strip() if title else "",
        "price": price
    })

print(f"Total SKU rows: {len(rows)}")
shared_count = sum(1 for x in rows if x['shared_asin'])
print(f"Rows where VC-ASIN == SL-ASIN (shared): {shared_count}")

# also rows where SL-ASIN is empty (no separate SL listing)
no_sl = sum(1 for x in rows if not x['sl_asin'])
print(f"Rows with empty SL-ASIN: {no_sl}")

# save for later
with open("vendor_table_data.json","w") as fo:
    json.dump(rows, fo, ensure_ascii=False, indent=2)

print("\n--- rows with shared ASIN (first 25) ---")
for x in rows:
    if x['shared_asin']:
        print(f"  {x['sku']}: VC={x['vc_asin']} SL={x['sl_asin']} shared={x['shared_asin']} price={x['price']}")
