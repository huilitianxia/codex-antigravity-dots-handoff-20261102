import csv
import openpyxl
import sys
from audit_all_22_families_buttons import by_asin, classify_asin_v4, all_by_sku, fba_by_sku, master_title_by_asin, master_model_by_asin

sys.stdout.reconfigure(encoding="utf-8")

fam_asins = {}
for asin, rlist in sorted(by_asin.items()):
    # Skip standalone 0-stock orphans that are not in any family
    skus = [str(r[2]) for r in rlist]
    fba_q = sum(fba_by_sku.get(s, 0) for s in skus)
    mfn_q = sum(int(all_by_sku.get(s, {}).get("quantity") or 0) for s in skus if all_by_sku.get(s, {}).get("fulfillment-channel") == "DEFAULT")
    has_parent = any(r[6] for r in rlist)
    if not has_parent and fba_q == 0 and mfn_q == 0:
        continue
    p = classify_asin_v4(asin, rlist)
    fam_asins.setdefault(p, []).append((asin, rlist, fba_q, mfn_q))

with open(r"D:\4A\00_当前工作区_202611\all_22_clean_summary.txt", "w", encoding="utf-8") as f:
    for p, alist in sorted(fam_asins.items()):
        active_cnt = sum(1 for _, _, fq, mq in alist if fq > 0 or mq > 0)
        f.write(f"\n==================== {p} (Total ASINs: {len(alist)} | In-Stock ASINs: {active_cnt}) ====================\n")
        for asin, rlist, fq, mq in alist:
            skus = [str(r[2]) for r in rlist]
            cur_p = str(rlist[0][6] or "ORPHAN")
            cur_c = str(rlist[0][58] or "")
            cur_s = str(rlist[0][59] or "")
            m_mod = master_model_by_asin.get(asin, "")
            m_tit = master_title_by_asin.get(asin, "") or str(rlist[0][8] or "")
            f.write(f"  ASIN={asin} | FBA={fq:4d} | MFN={mq:5d} | Mod={m_mod:16s} | CurP={cur_p:32s} | CurC={cur_c:20s} | CurS={cur_s:28s} | SKUs={skus} | T={m_tit[:65]}\n")

print("Wrote D:\\4A\\00_当前工作区_202611\\all_22_clean_summary.txt")
