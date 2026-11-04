import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';

const base = path.dirname(fileURLToPath(import.meta.url));
const plan = JSON.parse(await fs.readFile(path.join(base, 'campaign-cleanup-plan.json'), 'utf8'));
const selected = plan.campaigns.filter(row => row.decision === 'pause');
if (selected.length !== 101 || new Set(selected.map(row => row.id)).size !== 101) throw Error('Unexpected pause set');
if (selected.some(row => /REACTIVATE/.test(row.name))) throw Error('New exact tests selected for pause');
const out = 'E:/OpenAI-Codex/天皇のcodex/outputs/01a18a7c-7953-7b83-b51d-1a7f216ae7e1/20261103-ad-cleanup';
await fs.mkdir(out, {recursive: true});
const workbook = Workbook.create();
const groups = [
  ['Sponsored Products Campaigns', '商品推广活动', 'Sponsored Products'],
  ['Sponsored Display Campaigns', '展示型推广活动', 'Sponsored Display'],
];
const summary = [];
for (const [sheetName, sourceSheet, product] of groups) {
  const rows = selected.filter(row => row.sheet === sourceSheet);
  const values = [['Product','Entity','Operation','Campaign ID','State'], ...rows.map(row => [product,'Campaign','Update',row.id,'paused'])];
  const sheet = workbook.worksheets.add(sheetName);
  sheet.showGridLines = false;
  sheet.getRange(`A1:E${values.length}`).values = values;
  sheet.getRange(`A1:E${values.length}`).format.font = {name:'Arial',size:10};
  sheet.getRange(`A1:E${values.length}`).format.rowHeight = 22;
  sheet.getRange('A1:E1').format = {fill:'#203864',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'}};
  for (const [column,width] of [['A',25],['B',16],['C',15],['D',27],['E',14]]) sheet.getRange(`${column}1:${column}${values.length}`).format.columnWidth = width;
  sheet.getRange(`D2:D${values.length}`).setNumberFormat('@');
  sheet.freezePanes.freezeRows(1);
  summary.push({sheetName,count:rows.length});
}
workbook.recalculate();
for (const [sheetName] of groups) {
  const preview = await workbook.render({sheetName,range:'A1:E8',scale:1.5,format:'png'});
  await fs.writeFile(path.join(base, sheetName.startsWith('Sponsored Products')?'sp-upload-preview.png':'sd-upload-preview.png'), new Uint8Array(await preview.arrayBuffer()));
}
const inspect = await workbook.inspect({kind:'sheet,table',maxChars:2500,tableMaxRows:3,tableMaxCols:5});
const result = await SpreadsheetFile.exportXlsx(workbook);
const destination = path.join(out,'4A_PAUSE_101_OLD_CAMPAIGNS_20261103.xlsx');
await result.save(destination);
await fs.writeFile(path.join(base,'pause-upload-manifest.json'),JSON.stringify({destination,total:selected.length,sheets:summary,inspect:inspect.ndjson},null,2));
console.log(JSON.stringify({destination,total:selected.length,sheets:summary}));
