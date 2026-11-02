import openpyxl, glob, os, xlrd

WORK = r"C:\Users\24243\WorkBuddy\2026-07-24-20-10-20"
SRC = r"E:\xwechat_files\wxid_81xkainbu5d822_de43\msg\file\2026-07\3M价格.xls"
OUT = r"E:\xwechat_files\wxid_81xkainbu5d822_de43\msg\file\2026-07\3M价格_已填2026价.xlsx"

# 1. 读原 xls 全部数据
wb_src = xlrd.open_workbook(SRC)
sh = wb_src.sheet_by_index(0)
nrows, ncols = sh.nrows, sh.ncols
data = [[sh.cell_value(r, c) for c in range(ncols)] for r in range(nrows)]

# 2. 收集所有核对表（文件去重）
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
        # 特殊文件（终批生成的 Dispenser / ScotchTape）：无表头，列序
        # [行号, 原产品名, 2013价, 匹配ASIN, 亚马逊价格, ?, 置信度, 备注]
        for row in rows[1:]:
            if row[0] is None:
                continue
            rn = int(row[0])
            asin = row[3]
            price = row[4]
            conf = row[6]
            link = f"https://www.amazon.com/dp/{asin}" if asin else None
            candidates.setdefault(rn, []).append(
                (os.path.basename(f), asin, conf, price, link))
        continue
    ci = {str(h): i for i, h in enumerate(hdr)}
    def find_col(name):
        for i, h in enumerate(hdr):
            if h and name in str(h):
                return i
        return None
    ri = find_col("行号")
    ai = find_col("匹配ASIN")
    pi = find_col("亚马逊价格")
    li = find_col("亚马逊链接")
    cf = find_col("置信度")
    if any(v is None for v in (ri, ai, pi, li, cf)):
        print("WARN 跳过(列缺失):", os.path.basename(f), "ri", ri, "ai", ai, "pi", pi, "li", li, "cf", cf)
        print("   该文件 hdr:", hdr)
        continue
    for row in rows[1:]:
        if ri is None or row[ri] is None:
            continue
        rn = int(row[ri])
        candidates.setdefault(rn, []).append(
            (os.path.basename(f), row[ai], row[cf], row[pi], row[li]))

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

# 3. 写回新 xlsx
out = openpyxl.Workbook()
ws = out.active
ws.title = "Sheet1"
for c in range(ncols):
    ws.cell(1, c + 1, data[0][c])
ws.cell(1, ncols + 1, "匹配状态/ASIN/置信度")

filled = 0
nosale = 0
for r in range(1, nrows):
    for c in range(ncols):
        ws.cell(r + 1, c + 1, data[r][c])
    rn = r + 1
    ent = pick(rn)
    if ent:
        asin, conf, price, link = ent[1], ent[2], ent[3], ent[4]
        is_nosale = conf and any(k in str(conf) for k in ("无在售", "停产", "❌"))
        if is_nosale:
            ws.cell(r + 1, ncols + 1, f"无在售 | {conf}")
            nosale += 1
        else:
            pval = None
            if price is not None:
                s = str(price).replace("$", "").replace(",", "").strip()
                try:
                    pval = float(s)
                except Exception:
                    pval = None
            ws.cell(r + 1, 5, pval)          # E列 = 亚马逊价格
            ws.cell(r + 1, 6, link if link else None)  # F列 = 链接
            ws.cell(r + 1, ncols + 1, f"已匹配 | {asin} | {conf}")
            filled += 1

out.save(OUT)
print(f"核对表文件:{len(files)} | 候选行:{len(candidates)} | 已填充:{filled} | 无售:{nosale}")
print("已保存:", OUT)
