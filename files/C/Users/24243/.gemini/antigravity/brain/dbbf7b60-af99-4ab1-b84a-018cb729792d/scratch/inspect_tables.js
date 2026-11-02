const fs = require('fs');

function loadNdjson(filePath) {
  try {
    const lines = fs.readFileSync(filePath, 'utf8').trim().split('\n');
    return lines.map(l => {
      try { return JSON.parse(l); } catch(e) { return null; }
    }).filter(Boolean);
  } catch(e) { return []; }
}

const oosList = JSON.parse(fs.readFileSync('C:\\Users\\24243\\.gemini\\antigravity\\brain\\dbbf7b60-af99-4ab1-b84a-018cb729792d\\scratch\\oos_items.json', 'utf8'));

// Load VC audits and recovery records
const nd1 = loadNdjson('E:\\OpenAI-Codex\\Workspaces\\C-Documents\\2026-08-28\\new-task-handoff-2026-08-28\\outputs\\vc-sc-audit-20260830\\VC_SC全量商品审计与拿回计划_2026-08-30.xlsx.inspect.ndjson');
const nd2 = loadNdjson('E:\\OpenAI-Codex\\Workspaces\\C-Documents\\2026-08-28\\new-task-handoff-2026-08-28\\outputs\\remaining-33-after-3to4-20260905\\爸爸标记53款_剩余33款执行表_2026-09-05.xlsx.inspect.ndjson');
const nd3 = loadNdjson('E:\\OpenAI-Codex\\Workspaces\\C-Documents\\2026-08-28\\new-task-handoff-2026-08-28\\outputs\\father-marked-review-20260903\\爸爸标记商品_评分3至4分与SC同款对照_2026-09-03.xlsx.inspect.ndjson');
const nd4 = loadNdjson('E:\\OpenAI-Codex\\Workspaces\\C-Documents\\2026-08-28\\new-task-handoff-2026-08-28\\outputs\\all-recovered-32-20260831\\已全部拿回商品清单_32款_2026-08-31.xlsx.inspect.ndjson');

const asinDb = {};

function ingestTable(ndList, asinIdx, modelIdx, vcTotalIdx, vc2024Idx, ratingIdx, reviewsIdx, tag) {
  ndList.forEach(obj => {
    if (obj.kind === 'table' && obj.values) {
      obj.values.forEach(row => {
        const asin = row[asinIdx];
        if (asin && typeof asin === 'string' && asin.startsWith('B0')) {
          if (!asinDb[asin]) asinDb[asin] = { asin, sources: [] };
          asinDb[asin].sources.push(tag);
          if (row[modelIdx] && !asinDb[asin].model) asinDb[asin].model = row[modelIdx];
          if (row[vcTotalIdx] && !asinDb[asin].vcTotal) asinDb[asin].vcTotal = row[vcTotalIdx];
          if (row[vc2024Idx] && !asinDb[asin].vc2024) asinDb[asin].vc2024 = row[vc2024Idx];
          if (row[ratingIdx] && !asinDb[asin].rating) asinDb[asin].rating = row[ratingIdx];
          if (row[reviewsIdx] && !asinDb[asin].reviews) asinDb[asin].reviews = row[reviewsIdx];
        }
      });
    }
  });
}

// Inspect tables from nd1
nd1.filter(o => o.kind === 'table').forEach(t => {
  console.log('nd1 Table in sheet:', t.sheet, 'rows:', t.rows, 'first row:', t.values[0]?.slice(0, 8));
});
// Inspect tables from nd2
nd2.filter(o => o.kind === 'table').forEach(t => {
  console.log('nd2 Table in sheet:', t.sheet, 'rows:', t.rows, 'first row:', t.values[0]?.slice(0, 8));
});
