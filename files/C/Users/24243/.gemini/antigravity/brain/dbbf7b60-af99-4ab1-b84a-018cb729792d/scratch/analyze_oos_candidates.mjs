import fs from "node:fs";

const oosList = JSON.parse(fs.readFileSync('C:/Users/24243/.gemini/antigravity/brain/dbbf7b60-af99-4ab1-b84a-018cb729792d/scratch/oos_items.json', 'utf8'));
const vcSales = JSON.parse(fs.readFileSync("E:/OpenAI-Codex/Workspaces/C-Documents/2026-08-28/new-task-handoff-2026-08-28/work/vc_sales_audit_results.json", "utf8"));
const vcAudit = JSON.parse(fs.readFileSync("E:/OpenAI-Codex/Workspaces/C-Documents/2026-08-28/new-task-handoff-2026-08-28/work/vc_sc_audit_data.json", "utf8"));

// Build lookup maps by ASIN and by normalized SKU
const salesByAsin = new Map();
const salesBySku = new Map();

vcSales.all.forEach(r => {
  if (r.C) salesByAsin.set(r.C, r);
  if (r.B) {
    const normSku = String(r.B).toUpperCase().replace(/[^A-Z0-9]/g, '');
    salesBySku.set(normSku, r);
  }
});

const auditByAsin = new Map(vcAudit.vc_all.map(x => [x.vc_asin, x]));

console.log(`Analyzing ${oosList.length} out-of-stock items from first 3 pages...\n`);

const matchedOos = oosList.map(item => {
  const normSku = String(item.sku).toUpperCase().replace(/[^A-Z0-9]/g, '');
  const sales = salesByAsin.get(item.asin) || salesBySku.get(normSku) || {};
  const audit = auditByAsin.get(item.asin) || {};

  return {
    asin: item.asin,
    sku: item.sku,
    title: item.title,
    currentRank: item.rank,
    vcRank: sales.A || '--',
    vcSku: sales.B || audit.vc_sku || '--',
    totalUnits: sales.D ? Number(sales.D) : 0,
    totalRev: sales.E ? Number(sales.E) : 0,
    y2023: sales.AB ? Number(sales.AB) : 0,
    y2024: sales.AC ? Number(sales.AC) : 0,
    rating: audit.rating || '--',
    reviews: audit.reviews || '--',
  };
});

// Sort by VC historical units descending
matchedOos.sort((a, b) => b.totalUnits - a.totalUnits);

console.log('=== TOP HISTORICAL VC PERFORMERS AMONG OUT-OF-STOCK ITEMS ===\n');
matchedOos.slice(0, 30).forEach((m, idx) => {
  console.log(`${idx+1}. [${m.asin}] SKU: ${m.sku} (VC: ${m.vcSku}) | Units: ${m.totalUnits.toLocaleString()} | Rev: $${Math.round(m.totalRev).toLocaleString()} | 2024: ${m.y2024} | Rating: ${m.rating} (${m.reviews} reviews) | BSR: ${m.currentRank} | Title: ${m.title.slice(0, 45)}`);
});

fs.writeFileSync('C:/Users/24243/.gemini/antigravity/brain/dbbf7b60-af99-4ab1-b84a-018cb729792d/scratch/oos_matched_analysis.json', JSON.stringify(matchedOos, null, 2));
