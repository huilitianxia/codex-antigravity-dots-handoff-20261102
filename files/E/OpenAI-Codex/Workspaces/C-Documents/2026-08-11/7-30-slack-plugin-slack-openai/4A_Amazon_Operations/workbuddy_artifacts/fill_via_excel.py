import openpyxl, glob, os, win32com.client

WORK = r"C:\Users\24243\WorkBuddy\2026-07-24-20-10-20"
SRC = r"E:\xwechat_files\wxid_81xkainbu5d822_de43\msg\file\2026-07\3M价格_原版备份_20260807.xls"
OUT = r"E:\xwechat_files\wxid_81xkainbu5d822_de43\msg\file\2026-07\3M价格_已填2026价_带图.xlsx"

# ---- 收集 candidates（与 write_back.py 一致）----
files = sorted(set(glob.glob(os.path.join(WORK, "*核对表.xlsx")) +
                   glob.glob(os.path.join(WORK, "Tabs匹配*.xlsx"))))
PRIORITY = {
    103: "Notes_DesignerFashionista核对表.xlsx", 104: "Notes_DesignerFashionista核对表.xlsx",
    106: "Notes_DesignerFashionista核对表.xlsx", 107: "Notes_DesignerFashionista核对表.xlsx",
    120: "Notes_GreenerPrinted核对表.xlsx", 121: "Notes_GreenerPrinted核对表.xlsx",
    138: "Notes_Popup核对表.xlsx", 140: "Notes_Popup核对表.xlsx",
    141: "Notes_Popup核对表.xlsx", 155: "Notes_Popup核对表.xlsx",
}
candidates = {}
for f in files:
    wb = openpyxl.load_workbook(f, read_only=True, data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    hdr = rows[0]
    if hdr[0] is None:
        for row in rows[1:]:
            if row[0] is not None:
                rn = int(row[0]); asin = row[3]; price = row[4]; conf = row[6]
                link = f"https://www.amazon.com/dp/{asin}" if asin else None
                candidates.setdefault(rn, []).append((os.path.basename(f), asin, conf, price, link))
        continue
    def find_col(name):
        for i, h in enumerate(hdr):
            if h and name in str(h):
                return i
        return None
    ri = find_col("行号"); ai = find_col("匹配ASIN")
    pi = find_col("亚马逊价格"); li = find_col("亚马逊链接"); cf = find_col("置信度")
    for row in rows[1:]:
        if ri is None or row[ri] is None:
            continue
        rn = int(row[ri])
        candidates.setdefault(rn, []).append((os.path.basename(f), row[ai], row[cf], row[pi], row[li]))

def pick(rn):
    cands = candidates.get(rn, [])
    if not cands:
        return None
    pf = PRIORITY.get(rn)
    if pf:
        for c in cands:
            if c[0] == pf:
                return c
    for c in cands:
        if c[2] and "待另搜" not in str(c[2]):
            return c
    return cands[0]

# ---- Excel COM：打开原 xls（图片保留），填 E/F/G，另存 xlsx ----
xl = win32com.client.Dispatch("Excel.Application")
xl.Visible = False
xl.DisplayAlerts = False
wb = xl.Workbooks.Open(SRC)
ws = wb.Sheets(1)
try:
    pic_count = ws.Pictures().Count
except Exception:
    pic_count = "?"
print("原文件图片数:", pic_count)

filled = 0
nosale = 0
for rn in range(2, 170):  # 数据行 2-169
    ent = pick(rn)
    if not ent:
        continue
    asin, conf, price, link = ent[1], ent[2], ent[3], ent[4]
    is_nosale = conf and any(k in str(conf) for k in ("无在售", "停产", "❌"))
    if is_nosale:
        ws.Cells(rn, 7).Value = f"无在售 | {conf}"
        nosale += 1
    else:
        pval = None
        if price is not None:
            s = str(price).replace("$", "").replace(",", "").strip()
            try:
                pval = float(s)
            except Exception:
                pval = None
        ws.Cells(rn, 5).Value = pval
        ws.Cells(rn, 6).Value = link if link else None
        ws.Cells(rn, 7).Value = f"已匹配 | {asin} | {conf}"
        filled += 1

wb.SaveAs(OUT, FileFormat=51)  # 51 = xlsx
wb.Close(False)
xl.Quit()
print(f"filled={filled} nosale={nosale}")
print("已保存(带图):", OUT)
