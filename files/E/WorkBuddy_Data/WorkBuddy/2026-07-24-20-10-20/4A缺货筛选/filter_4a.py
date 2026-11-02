# -*- coding: utf-8 -*-
"""4A 缺货补货一键筛选工具
用法：把卖家精灵「品牌分析」导出的 Excel 放进同目录 input/ 文件夹，双击 run_筛选.bat。
输出：output/4A缺货补货清单_已筛.xlsx（含「补货清单」+「统计」两个表）。
逻辑：自动识别 评分 / 上架状态 等列 -> 筛选 评分>=4.0 且 缺货/不可售 -> 按 月销量、评分数 降序。
"""
import os
import glob
import openpyxl

BASE = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE, "input")
OUTPUT_DIR = os.path.join(BASE, "output")

RATING_MIN = 4.0
OOS_KEYWORDS = ["不可售", "缺货", "无货", "下架", "停售", "暂时不可", "暂时缺",
                "unavailable", "out of stock", "currently unavailable", "oos", "not available"]

CANON = {
    "asin":   ["asin"],
    "brand":  ["品牌", "brand"],
    "title":  ["标题", "商品标题", "title", "name", "商品名称"],
    "rating": ["评分", "星级", "rating", "star", "得分", "评价分"],
    "reviews":["评分数", "评论数", "review", "评价数", "评价数量"],
    "sales":  ["月销量", "销量", "sales", "monthly", "月均销量"],
    "price":  ["价格", "price", "售价"],
    "status": ["状态", "库存", "上架", "可售", "availability", "stock", "sold", "在售", "售卖状态"],
}


def norm(s):
    return str(s).strip().lower() if s is not None else ""


STATUS_KEYS = ["状态", "可售", "库存状态", "在售状态", "售卖状态",
                "availability", "stock status", "is available", "sold"]


def is_status_header(h):
    hl = norm(h)
    # 排除"上架时间/上架天数/上架日期"这类日期列，避免误判为库存状态
    if any(bad in hl for bad in ["时间", "天数", "日期"]):
        return False
    return any(k in hl for k in STATUS_KEYS)


def is_rating_header(h):
    hl = norm(h)
    # 排除"评分数/评论数"等计数列，避免把评论数当成评分
    if "数" in hl or "count" in hl or "review" in hl:
        return False
    return any(k in hl for k in ["评分", "星级", "rating", "star", "得分"])


def is_reviews_header(h):
    hl = norm(h)
    return any(k in hl for k in ["评分数", "评论数", "评价数", "review count", "reviews", "评价数量"])


def map_columns(header):
    idx = {}
    for canon, keys in CANON.items():
        for i, h in enumerate(header):
            if h is None:
                continue
            if canon == "status":
                if is_status_header(h):
                    idx[canon] = i
                    break
            elif canon == "rating":
                if is_rating_header(h):
                    idx[canon] = i
                    break
            elif canon == "reviews":
                if is_reviews_header(h):
                    idx[canon] = i
                    break
            else:
                if any(k in norm(h) for k in keys):
                    idx[canon] = i
                    break
    return idx


def is_oos(status_val, price_val):
    if status_val not in (None, ""):
        s = norm(status_val)
        for k in OOS_KEYWORDS:
            if k in s:
                return True, "状态列命中「%s」" % status_val
    if price_val in (None, "") or (isinstance(price_val, (int, float)) and price_val == 0):
        return True, "价格列为空（缺货候选，未确认状态列）"
    return False, ""


def to_float(v):
    try:
        return float(str(v).replace("$", "").replace(",", "").strip())
    except Exception:
        return None


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    files = sorted(glob.glob(os.path.join(INPUT_DIR, "*.xlsx")))
    if not files:
        print("未找到 input/ 下的 Excel。请把 4A 品牌分析导出放进 input/ 文件夹再运行。")
        return

    collected = []
    stats = {"files": 0, "rows": 0, "rating_ok": 0, "oos": 0, "final": 0, "no_status_warn": False}

    for f in files:
        wb = openpyxl.load_workbook(f, read_only=True, data_only=True)
        target = None
        header = None
        hrow = 1
        for ws in wb.worksheets:
            for r in range(1, 12):
                row = [ws.cell(r, c).value for c in range(1, ws.max_column + 1)]
                if any(norm(v) == "asin" for v in row if v is not None):
                    target = ws
                    header = row
                    hrow = r
                    break
            if target:
                break
        if not target:
            target = wb.worksheets[0]
            header = [target.cell(1, c).value for c in range(1, target.max_column + 1)]
            hrow = 1

        col = map_columns(header)
        if "rating" not in col:
            print("[警告] %s 未找到评分列，跳过评分筛选。" % os.path.basename(f))
        if "status" not in col:
            stats["no_status_warn"] = True
            print("[提示] %s 未找到库存状态列，将用『价格为空』作为缺货候选（可能含未销售款）。" % os.path.basename(f))

        ri = col.get("rating")
        si = col.get("status")
        pi = col.get("price")
        ti = col.get("title")
        ai = col.get("asin")
        bi = col.get("brand")
        sali = col.get("sales")
        revi = col.get("reviews")

        rows = list(target.iter_rows(min_row=hrow + 1, values_only=True))
        # 卖家精灵有时把评分存成 44 (=4.4)，自动侦测并还原
        raw_ratings = [to_float(r[ri]) for r in rows
                       if ri is not None and r[ri] not in (None, "")]
        rscale = 0.1 if raw_ratings and max(raw_ratings) > 10 else 1.0
        stats["files"] += 1
        for row in rows:
            if not any(c not in (None, "") for c in row):
                continue
            stats["rows"] += 1
            if ri is not None:
                rv = to_float(row[ri])
                if rv is not None:
                    rv = rv * rscale
                if rv is None or rv < RATING_MIN:
                    continue
            stats["rating_ok"] += 1
            oos, reason = is_oos(row[si] if si is not None else None,
                                 row[pi] if pi is not None else None)
            if not oos:
                continue
            stats["oos"] += 1
            collected.append({
                "asin": row[ai] if ai is not None else "",
                "brand": row[bi] if bi is not None else "",
                "title": row[ti] if ti is not None else "",
                "rating": (to_float(row[ri]) * rscale) if (ri is not None and row[ri] not in (None, "")) else "",
                "reviews": row[revi] if revi is not None else "",
                "sales": row[sali] if sali is not None else "",
                "price": row[pi] if pi is not None else "",
                "status": row[si] if si is not None else "",
                "signal": reason,
            })
            stats["final"] += 1

    seen = set()
    uniq = []
    for r in collected:
        k = r["asin"]
        if k and k in seen:
            continue
        seen.add(k)
        uniq.append(r)

    def num(v):
        x = to_float(v)
        return x if x is not None else -1

    uniq.sort(key=lambda r: (num(r["sales"]), num(r["reviews"])), reverse=True)

    out = os.path.join(OUTPUT_DIR, "4A缺货补货清单_已筛.xlsx")
    wb2 = openpyxl.Workbook()
    ws = wb2.active
    ws.title = "补货清单"
    cols = ["ASIN", "品牌", "商品标题", "评分", "评分数", "月销量", "价格($)", "上架状态", "缺货信号"]
    ws.append(cols)
    for r in uniq:
        ws.append([r["asin"], r["brand"], r["title"], r["rating"], r["reviews"],
                   r["sales"], r["price"], r["status"], r["signal"]])

    ws2 = wb2.create_sheet("统计")
    ws2.append(["指标", "数值"])
    ws2.append(["处理文件数", stats["files"]])
    ws2.append(["读取数据行", stats["rows"]])
    ws2.append(["评分>=4.0 行", stats["rating_ok"]])
    ws2.append(["其中缺货/不可售", stats["oos"]])
    ws2.append(["去重后补货清单数", len(uniq)])
    wb2.save(out)

    print("\n完成！补货清单已生成：%s" % out)
    print("  处理文件=%d 数据行=%d 评分>=4.0=%d 缺货=%d 去重后=%d"
          % (stats["files"], stats["rows"], stats["rating_ok"], stats["oos"], len(uniq)))
    if stats["no_status_warn"]:
        print("  [注意] 部分文件无库存状态列，缺货判定用了『价格为空』近似，请人工复核。")


if __name__ == "__main__":
    main()
