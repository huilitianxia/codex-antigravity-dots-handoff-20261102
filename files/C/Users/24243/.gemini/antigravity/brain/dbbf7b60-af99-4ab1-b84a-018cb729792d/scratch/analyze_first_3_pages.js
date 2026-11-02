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

const activeWithStock = all.filter(i => i.status === '在售' && parseInt(i.avail || '0', 10) > 0);
const outOfStock = all.filter(i => i.status === '缺货');
const suppressed = all.filter(i => i.status && i.status.includes('禁止'));
const other = all.filter(i => i.status !== '在售' && i.status !== '缺货' && (!i.status || !i.status.includes('禁止')));

console.log('=== SUMMARY OF FIRST 3 PAGES (73 ITEMS) ===');
console.log(`Active with Stock: ${activeWithStock.length}`);
console.log(`Out of Stock: ${outOfStock.length}`);
console.log(`Suppressed: ${suppressed.length}`);
console.log(`Other: ${other.length}`);

console.log('\n--- ACTIVE WITH STOCK DETAILS ---');
activeWithStock.forEach(i => {
  console.log(JSON.stringify({
    asin: i.asin,
    sku: i.sku,
    avail: i.avail,
    price: i.price,
    b2bPrice: i.b2bPrice,
    rank: i.rank,
    title: (i.title || '').replace(/^\d{4}年\d+月\d+日\s+\d{2}:\d{2}\s*/g, '').slice(0, 70)
  }, null, 2));
});

console.log('\n--- SUPPRESSED ITEMS ---');
suppressed.forEach(i => {
  console.log(`${i.asin} | ${i.sku} | ${i.status} | ${(i.title || '').slice(0, 60)}`);
});
