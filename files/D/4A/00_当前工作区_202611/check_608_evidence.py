import openpyxl
import os

print("=== CHECKING 2026 MASTER FOR 608 ===")
wb = openpyxl.load_workbook(r'C:\Users\24243\Downloads\亚马逊供应商和开店总表-2026 (3).xlsx', data_only=True)
ws = wb['Sheet1']
for r in range(2, ws.max_row + 1):
    sku = str(ws.cell(r, 1).value)
    if '608' in sku or '037' in sku or '039' in sku or '040' in sku:
        r_str = ' | '.join([str(ws.cell(r, c).value) for c in range(1, 10) if ws.cell(r, c).value is not None])
        print(f"Row {r}: {r_str}")
wb.close()

print("\n=== CHECKING 印刷用图片 FOR 608 / 037 / 039 / 040 / 0166 / 66114 ===")
terms = ['608', '037', '039', '040', '0166', '8078', '66114']
matches = []
for root, dirs, files in os.walk(r'D:\4A\印刷用图片'):
    for f in files:
        for t in terms:
            if t in f:
                matches.append((t, os.path.join(root, f)))
                break
print(f"Found {len(matches)} files in 印刷用图片. First 20:")
for t, p in matches[:20]:
    print(f"  [{t}] {p}")
