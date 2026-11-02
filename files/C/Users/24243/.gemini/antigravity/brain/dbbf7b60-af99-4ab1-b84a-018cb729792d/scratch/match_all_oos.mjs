import fs from "node:fs";

const oosList = JSON.parse(fs.readFileSync('C:/Users/24243/.gemini/antigravity/brain/dbbf7b60-af99-4ab1-b84a-018cb729792d/scratch/oos_items.json', 'utf8'));
const vcSales = JSON.parse(fs.readFileSync("E:/OpenAI-Codex/Workspaces/C-Documents/2026-08-28/new-task-handoff-2026-08-28/work/vc_sales_audit_results.json", "utf8"));

function loadNdjson(filePath) {
  try {
    const lines = fs.readFileSync(filePath, 'utf8').trim().split('\n');
    return lines.map(l => {
      try { return JSON.parse(l); } catch(e) { return null; }
    }).filter(Boolean);
  } catch(e) { return []; }
}

const rem33 = loadNdjson('E:/OpenAI-Codex/Workspaces/C-Documents/2026-08-28/new-task-handoff-2026-08-28/outputs/remaining-33-after-3to4-20260905/爸爸标记53款_剩余33款执行表_2026-09-05.xlsx.inspect.ndjson');
const dad53 = loadNdjson('E:/OpenAI-Codex/Workspaces/C-Documents/2026-08-28/new-task-handoff-2026-08-28/outputs/father-marked-review-20260903/爸爸标记商品_评分3至4分与SC同款对照_2026-09-03.xlsx.inspect.ndjson');
const rec32 = loadNdjson('E:/OpenAI-Codex/Workspaces/C-Documents/2026-08-28/new-task-handoff-2026-08-28/outputs/all-recovered-32-20260831/已全部拿回商品清单_32款_2026-08-31.xlsx.inspect.ndjson');

const extraDb = new Map();

function addTable(ndList, tag) {
  ndList.forEach(obj => {
    if (obj.kind === 'table' && obj.values) {
      obj.values.slice(3).forEach(r => {
        // scan row for ASIN
        const asin = r.find(c => typeof c === 'string' && /^B0[A-Z0-9]{8}$/.test(c));
        if (asin) {
          if (!extraDb.has(asin)) extraDb.set(asin, { asin, tag, row: r });
        }
      });
    }
  });
}

addTable(rem33, 'rem33');
addTable(dad53, 'dad53');
addTable(rec32, 'rec32');

// Build sales lookups
const salesByAsin = new Map(vcSales.all.filter(r => r.C).map(r => [r.C, r]));
const salesByCleanSku = new Map();
vcSales.all.forEach(r => {
  if (r.B) {
    const k = String(r.B).toUpperCase().replace(/[^A-Z0-9]/g, '');
    salesByCleanSku.set(k, r);
  }
});

const enriched = oosList.map(item => {
  let s = salesByAsin.get(item.asin);
  if (!s) {
    const clean = String(item.sku).toUpperCase().replace(/FBA/g, '').replace(/[^A-Z0-9]/g, '');
    s = salesByCleanSku.get(clean);
  }
  const extra = extraDb.get(item.asin);

  return {
    asin: item.asin,
    sku: item.sku,
    cleanTitle: item.title,
    currentRank: item.rank,
    totalUnits: s ? Number(s.D) : 0,
    totalRev: s ? Number(s.E) : 0,
    y2023: s ? Number(s.AB) : 0,
    y2024: s ? Number(s.AC) : 0,
    vcSku: s ? s.B : (extra ? extra.row[1] : '--'),
    rating: (extra && extra.row[3] && !isNaN(Number(extra.row[3]))) ? extra.row[3] : (extra && extra.row[5] ? extra.row[5] : '--'),
    reviews: (extra && extra.row[4] && !isNaN(Number(extra.row[4]))) ? extra.row[4] : (extra && extra.row[6] ? extra.row[6] : '--'),
    tag: extra ? extra.tag : '--'
  };
});

enriched.sort((a, b) => b.totalUnits - a.totalUnits);

console.log('=== ALL 43 OUT OF STOCK CANDIDATES RANKED BY VC HISTORICAL UNITS ===\n');
enriched.forEach((m, idx) => {
  console.log(`${idx+1}. [${m.asin}] ${m.sku} (VC: ${m.vcSku}) | Units: ${m.totalUnits.toLocaleString()} | Rev: $${Math.round(m.totalRev).toLocaleString()} | 2024: ${m.y2024} | 2023: ${m.y2023} | Rating: ${m.rating} (${m.reviews} revs) | BSR: ${m.currentRank}`);
});

fs.writeFileSync('C:/Users/24243/.gemini/antigravity/brain/dbbf7b60-af99-4ab1-b84a-018cb729792d/scratch/enriched_oos.json', JSON.stringify(enriched, null, 2));
