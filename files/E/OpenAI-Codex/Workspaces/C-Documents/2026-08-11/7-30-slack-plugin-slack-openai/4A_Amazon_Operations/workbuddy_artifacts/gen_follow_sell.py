import json, openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

# Load matched data
with open("ss_matched.json") as f:
    ss = json.load(f)
with open("vendor_table_data.json") as f:
    vdata = json.load(f)

# build shared flag map
shared_map = {a: True for x in vdata for a in x['shared_asin']}

def to_float(v):
    try: return float(v)
    except: return None

confirmed = []   # sellers>=2 and rating>=4.0 and reviews>=50
verify = []      # rating>=4.0 and reviews>=50 and (sellers<=1 or unknown) -> need manual test

for a, rec in ss.items():
    rating = to_float(rec['rating'])
    reviews = to_float(rec['reviews'])
    sellers = to_float(rec['sellers'])
    sales = to_float(rec['monthly_sales'])
    rec['rating_f'] = rating
    rec['reviews_f'] = reviews
    rec['sellers_f'] = sellers
    rec['shared'] = a in shared_map
    if rating is not None and reviews is not None and rating >= 4.0 and reviews >= 50:
        if sellers is not None and sellers >= 2:
            confirmed.append((a, rec))
        else:
            verify.append((a, rec))

# sort: confirmed by reviews desc; verify by reviews desc
confirmed.sort(key=lambda x: x[1]['reviews_f'] or 0, reverse=True)
verify.sort(key=lambda x: x[1]['reviews_f'] or 0, reverse=True)

wb = openpyxl.Workbook()
thin = Side(style='thin', color='BBBBBB')
border = Border(left=thin,right=thin,top=thin,bottom=thin)
hdr_fill = PatternFill('solid', fgColor='1F4E78')
hdr_font = Font(bold=True, color='FFFFFF')
title_font = Font(bold=True, size=13, color='1F4E78')

def style_header(ws, ncols, row=1):
    for c in range(1, ncols+1):
        cell = ws.cell(row=row, column=c)
        cell.fill = hdr_fill; cell.font = hdr_font
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        cell.border = border

def write_sheet(ws, data, title, note):
    ws.cell(row=1, column=1, value=title).font = title_font
    ws.cell(row=2, column=1, value=note).font = Font(italic=True, color='666666')
    headers = ["VC-ASIN","SKU","产品标题(略)","评分","评论数","卖家数","BuyBox卖家","月销量(估算)","是否共用ASIN(VC=SL)","结论/建议"]
    ws.append([])  # row3 placeholder
    for i,h in enumerate(headers,1):
        ws.cell(row=3, column=i, value=h)
    style_header(ws, len(headers), row=3)
    r = 4
    for a, rec in data:
        ws.cell(row=r, column=1, value=a)
        ws.cell(row=r, column=2, value=rec['sku'])
        title_txt = rec.get('source_file','')
        ws.cell(row=r, column=3, value="(见供应商总表)")
        ws.cell(row=r, column=4, value=rec['rating_f'])
        ws.cell(row=r, column=5, value=rec['reviews_f'])
        ws.cell(row=r, column=6, value=rec['sellers_f'])
        ws.cell(row=r, column=7, value=rec['buybox'])
        ws.cell(row=r, column=8, value=rec['monthly_sales'])
        ws.cell(row=r, column=9, value="是" if rec['shared'] else "否")
        if a in confirmed_asin_list:
            ws.cell(row=r, column=10, value="已确认可跟卖(卖家数≥2)")
        else:
            ws.cell(row=r, column=10, value="需Seller Central测试能否添加offer")
        for c in range(1, len(headers)+1):
            ws.cell(row=r, column=c).border = border
            ws.cell(row=r, column=c).alignment = Alignment(vertical='center', wrap_text=True)
        r += 1
    # widths
    widths = [14,14,18,8,9,8,22,12,18,30]
    for i,w in enumerate(widths,1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w

confirmed_asin_list = [a for a,_ in confirmed]

ws1 = wb.active
ws1.title = "已确认可跟卖"
write_sheet(ws1, confirmed, "已确认可跟卖且数据不错（卖家数≥2、评分≥4.0、评论≥50）",
            "判断依据：卖家精灵显示卖家数≥2，即已有3P跟卖，亚马逊允许。可直接补货独享VC好数据。")

ws2 = wb.create_sheet("高数据待验证")
write_sheet(ws2, verify, "高数据但需手动验证（评分≥4.0、评论≥50，目前卖家数≤1）",
            "这些款评分/评论不错，但目前只有Amazon或自家在卖(卖家数=1)。是否允许跟卖需在Seller Central【添加商品】搜ASIN测试。")

wb.save(r"E:/Desktop/4A_VC可跟卖检测_2026-08-11.xlsx")
print(f"Confirmed (already can follow-sell): {len(confirmed)}")
for a,rec in confirmed:
    print(f"  {a} [{rec['sku']}] rating={rec['rating_f']} reviews={rec['reviews_f']} sellers={rec['sellers_f']} buybox={rec['buybox']} shared={rec['shared']}")
print(f"\nVerify (high data, manual test): {len(verify)}")
for a,rec in verify[:15]:
    print(f"  {a} [{rec['sku']}] rating={rec['rating_f']} reviews={rec['reviews_f']} sellers={rec['sellers_f']} buybox={rec['buybox']} shared={rec['shared']}")
print("\nSaved: E:/Desktop/4A_VC可跟卖检测_2026-08-11.xlsx")
