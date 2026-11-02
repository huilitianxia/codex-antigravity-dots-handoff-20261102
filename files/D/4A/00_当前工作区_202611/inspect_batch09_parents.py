import openpyxl

wb_09 = openpyxl.load_workbook(r'D:\4A\00_Codex交接给Gemini_20261101\03_正式上传文件\09-21-families-clean-reclassification.xlsm', read_only=True, data_only=True)
ws_09 = wb_09['Template']
parents_21 = {}
for r in ws_09.iter_rows(min_row=7, values_only=True):
    sku = str(r[2] or '').strip()
    plevel = str(r[5] or '').strip()
    if plevel == 'Parent':
        parents_21[sku] = {
            'sku': sku,
            'theme': str(r[7] or '').strip(),
            'title': str(r[8] or '').strip(),
            'prod_type': str(r[0] or '').strip()
        }

print(f"21 Parents from Batch 09 ({len(parents_21)}):")
for k, v in sorted(parents_21.items()):
    print(f"  {k:36s} | Theme={v['theme']:12s} | Type={v['prod_type']:20s} | Title={v['title']}")
