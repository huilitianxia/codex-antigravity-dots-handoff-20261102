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

console.log('Page 1 count:', p1.length);
console.log('Page 2 count:', p2.length);
console.log('Page 3 count:', p3.length);

const all = [...p1, ...p2, ...p3];
console.log('Total across 3 pages:', all.length);

console.log('\n================ ALL ITEMS ================');
all.forEach((item, idx) => {
  console.log(`${idx+1}. [${item.status}] ASIN: ${item.asin} | SKU: ${item.sku} | Avail: ${item.avail} | Inbound: ${item.inbound} | Price: ${item.price} | Title: ${(item.title || '').slice(0, 50)}`);
});
