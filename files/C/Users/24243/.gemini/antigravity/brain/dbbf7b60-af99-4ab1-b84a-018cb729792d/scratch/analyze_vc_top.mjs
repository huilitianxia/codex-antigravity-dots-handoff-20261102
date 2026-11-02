import fs from "node:fs";
const vcSales = JSON.parse(fs.readFileSync("E:/OpenAI-Codex/Workspaces/C-Documents/2026-08-28/new-task-handoff-2026-08-28/work/vc_sales_audit_results.json", "utf8"));
const vcAudit = JSON.parse(fs.readFileSync("E:/OpenAI-Codex/Workspaces/C-Documents/2026-08-28/new-task-handoff-2026-08-28/work/vc_sc_audit_data.json", "utf8"));
const auditMap = new Map(vcAudit.vc_all.map(x => [x.vc_asin, x]));

const top15VC = vcSales.all.slice(0, 15).map(r => {
  const a = auditMap.get(r.C) || {};
  return {
    rank: r.A,
    sku: r.B,
    asin: r.C,
    totalUnits: Number(r.D),
    totalRev: Number(r.E),
    y2023: Number(r.AB),
    y2024: Number(r.AC),
    scMatchClass: a.sc_match_class || "未在8月VC表",
    scAsins: a.sc_match_asins || "",
    rating: a.rating,
    reviews: a.review_count
  };
});
console.log(JSON.stringify({
  vcGrandTotalUnits: vcSales.stats.sums.D,
  vcGrandTotalRev: vcSales.stats.sums.E,
  vcYearlyUnits: {
    2015: vcSales.stats.sums.T,
    2016: vcSales.stats.sums.U,
    2017: vcSales.stats.sums.V,
    2018: vcSales.stats.sums.W,
    2019: vcSales.stats.sums.X,
    2020: vcSales.stats.sums.Y,
    2021: vcSales.stats.sums.Z,
    2022: vcSales.stats.sums.AA,
    2023: vcSales.stats.sums.AB,
    2024: vcSales.stats.sums.AC
  },
  top15VC
}, null, 2));
