import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';
const base = path.dirname(fileURLToPath(import.meta.url));
const plan = JSON.parse(await fs.readFile(path.join(base, process.argv[2] ?? 'optimization-approved-plan-US20261103.json'), 'utf8'));
const headers = ['Product','Entity','Operation','Campaign ID','Ad Group ID','Keyword ID','State','Daily Budget','Bid','Keyword Text','Match Type'];
const values = [headers, ...plan.rows.map(r => headers.map(h => r[h] ?? null))];
const wb = Workbook.create();
const s = wb.worksheets.add('Sponsored Products Campaigns');
s.getRange(`A1:K${values.length}`).values = values;
s.getRange(`A1:K${values.length}`).format.font = {name:'Arial',size:10};
s.getRange(`A1:K${values.length}`).format.rowHeight = 24;
s.getRange('A1:K1').format = {fill:'#203864',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'}};
for (const [col, width] of [['A',25],['B',16],['C',15],['D',24],['E',24],['F',24],['G',14],['H',18],['I',12],['J',52],['K',16]]) {
  s.getRange(`${col}1:${col}${values.length}`).format.columnWidth = width;
}
s.getRange(`D2:F${values.length}`).setNumberFormat('0');
s.getRange(`H2:I${values.length}`).setNumberFormat('0.00');
s.freezePanes.freezeRows(1);
wb.recalculate();
const inspection = await wb.inspect({kind:'region',sheetId:s.name,range:`A1:K${values.length}`,maxChars:3500,tableMaxRows:7,tableMaxCols:11});
await fs.writeFile(path.join(base,'optimization-upload-inspection.ndjson'),inspection.ndjson);
for (const [range,name] of [[`A1:I${Math.min(11,values.length)}`,'budget'],[`F${Math.max(2,values.length-9)}:K${values.length}`,'keywords']]) {
  const image = await wb.render({sheetName:s.name,range,scale:1.3,format:'png'});
  await fs.writeFile(path.join(base,`optimization-upload-${name}.png`),new Uint8Array(await image.arrayBuffer()));
}
const output = path.resolve(base,'../../outputs/01a18a7c-7953-7b83-b51d-1a7f216ae7e1/20261103-ad-optimization');
await fs.mkdir(output,{recursive:true});
const filename = path.join(output,plan.output_filename ?? '4A_US_AD_OPTIMIZATION_20261103.xlsx');
await(await SpreadsheetFile.exportXlsx(wb)).save(filename);
await fs.writeFile(path.join(base,'optimization-upload-manifest.json'),JSON.stringify({filename,rows:plan.rows.length,budget_after:plan.budget_after,headers},null,2));
console.log(JSON.stringify({filename,rows:plan.rows.length,budget_after:plan.budget_after}));
