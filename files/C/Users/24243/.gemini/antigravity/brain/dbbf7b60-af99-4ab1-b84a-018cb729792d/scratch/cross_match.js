const fs = require('fs');

// We have the 26 active items
const activeAsins = [
  "B0CPM4CP6T", "B07T42J6FY", "B01LPKL5IE", "B07T79KGWF", "B07DJG1W71",
  "B00SMEE3XQ", "B07DJXC4PJ", "B07Z2555TN", "B073VPHSJ9", "B07DLM2QP1",
  "B07T42DXZ1", "B00SMEE5HU", "B073VPFBL6", "B07J6Q5TTR", "B07JVSYNYV",
  "B01M986R0Y", "B07HDVVZ1B", "B07DJP6SNG", "B01M3N310M", "B07T55QCRY",
  "B00SMEEN40", "B00SMEEVC4", "B00SMEEVCO", "B00SMEEV4C", "B01LVTWP7Q",
  "B01MZ4FDN5"
];

// Let's check the recovered-32 ndjson and remaining-33 ndjson
function loadNdjson(filePath) {
  try {
    const lines = fs.readFileSync(filePath, 'utf8').trim().split('\n');
    return lines.map(l => {
      try { return JSON.parse(l); } catch(e) { return null; }
    }).filter(Boolean);
  } catch(e) { return []; }
}

const rec32 = loadNdjson('E:\\OpenAI-Codex\\Workspaces\\C-Documents\\2026-08-28\\new-task-handoff-2026-08-28\\outputs\\all-recovered-32-20260831\\已全部拿回商品清单_32款_2026-08-31.xlsx.inspect.ndjson');
const rem33 = loadNdjson('E:\\OpenAI-Codex\\Workspaces\\C-Documents\\2026-08-28\\new-task-handoff-2026-08-28\\outputs\\remaining-33-after-3to4-20260905\\爸爸标记53款_剩余33款执行表_2026-09-05.xlsx.inspect.ndjson');

const table32 = rec32.find(o => o.kind === 'table' && o.sheet === '已全部拿回32');
const table33 = rem33.find(o => o.kind === 'table' && o.sheet === '剩余33款');

const mapInfo = {};

if (table32 && table32.values) {
  table32.values.slice(4).forEach(row => {
    const asin = row[1];
    if (asin) {
      mapInfo[asin] = {
        asin,
        sku: row[2],
        desc: row[4],
        rating: row[5],
        reviews: row[6],
        source: '暑期已拿回32款'
      };
    }
  });
}

if (table33 && table33.values) {
  table33.values.slice(4).forEach(row => {
    const asin = row[8];
    const sku = row[1];
    if (asin) {
      mapInfo[asin] = {
        asin,
        sku,
        desc: row[2],
        rating: row[3],
        reviews: row[4],
        vcHistoryUnits: row[5],
        source: '爸爸标记33款'
      };
    }
  });
}

console.log('--- MATCHING 26 ACTIVE ITEMS WITH HISTORICAL METRICS ---');
const matched = [];
activeAsins.forEach(asin => {
  const info = mapInfo[asin] || { asin, desc: '未在32/33表中匹配', rating: '--', reviews: '--' };
  matched.push(info);
});

console.log(JSON.stringify(matched, null, 2));
