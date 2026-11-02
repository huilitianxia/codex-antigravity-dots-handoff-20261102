const fs = require('fs');

function extractJson(filePath) {
  try {
    const txt = fs.readFileSync(filePath, 'utf8');
    const start = txt.indexOf('```json');
    const end = txt.lastIndexOf('```');
    if (start !== -1 && end !== -1 && end > start) {
      const jsonStr = txt.slice(start + 7, end).trim();
      const data = JSON.parse(jsonStr);
      return Array.isArray(data) ? data : (data.items || []);
    }
  } catch(e) {
    console.error('Error reading', filePath, e.message);
  }
  return [];
}

const p1 = extractJson('C:\\Users\\24243\\.gemini\\antigravity\\brain\\f1367eb9-fa19-4a11-abf4-4dc63e32dd4b\\.system_generated\\steps\\581\\output.txt');
const p2 = extractJson('C:\\Users\\24243\\.gemini\\antigravity\\brain\\f1367eb9-fa19-4a11-abf4-4dc63e32dd4b\\.system_generated\\steps\\570\\output.txt');
const p3 = extractJson('C:\\Users\\24243\\.gemini\\antigravity\\brain\\f1367eb9-fa19-4a11-abf4-4dc63e32dd4b\\.system_generated\\steps\\588\\output.txt');

const all = [...p1, ...p2, ...p3];
const oos = all.filter(i => i.status === '缺货');

console.log('Out of stock items count in first 3 pages:', oos.length);

const oosList = oos.map(i => ({
  asin: i.asin,
  sku: i.sku,
  fnsku: i.fnsku,
  rank: i.rank,
  title: (i.title || '').replace(/^\d{4}年\d+月\d+日\s+\d{2}:\d{2}\s*/g, '').replace(/^\d{4}年\d+月\d+日\s+\d{2}:\d{2}\s*/g, '').trim()
}));

fs.writeFileSync('C:\\Users\\24243\\.gemini\\antigravity\\brain\\dbbf7b60-af99-4ab1-b84a-018cb729792d\\scratch\\oos_items.json', JSON.stringify(oosList, null, 2));
console.log('Saved to oos_items.json');
