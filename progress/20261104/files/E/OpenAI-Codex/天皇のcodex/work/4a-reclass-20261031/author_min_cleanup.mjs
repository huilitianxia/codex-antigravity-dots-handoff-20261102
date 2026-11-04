import fs from 'node:fs/promises';
import {FileBlob, SpreadsheetFile} from '@oai/artifact-tool';
const root = 'E:/OpenAI-Codex/天皇のcodex/work/4a-reclass-20261031';
const source = 'D:/下载文件/PriceAndQuantity.xlsm';
const final = 'E:/OpenAI-Codex/天皇のcodex/outputs/01a18a7c-7953-7b83-b51d-1a7f216ae7e1/20261031-urgent-fixes/05-remove-temporary-minimums.xlsm';
const mode = process.argv[2] || 'before';
const wb = await SpreadsheetFile.importXlsx(await FileBlob.load(mode === 'verify' ? final : source));
const sheet = wb.worksheets.getItem('Template');
const rows = [
  ['AAAA 4A 303-AC-holder', 17.99],
  ['AAAA 4A 6032', 24.99],
  ['AAAA 4A 608-N-L-210', 14.99],
  ['303-AC-holder', 11.60],
];
const deletion = 'Delete Minimum Seller Allowed Price (Sell on Amazon, US)';
if (mode === 'author') {
  sheet.getRange('A7:A10').values = rows.map(r => [r[0]]);
  sheet.getRange('G7:G10').values = rows.map(r => [r[1]]);
  sheet.getRange('I7:I10').values = rows.map(() => [deletion]);
  wb.recalculate();
  await (await SpreadsheetFile.exportXlsx(wb)).save(`${root}/05-min-cleanup-authored-cells.xlsx`);
  await fs.writeFile(`${root}/05-min-cleanup-spec.json`, JSON.stringify({source, final, rows, deletion}, null, 2));
  console.log((await wb.inspect({kind:'table', range:'Template!A7:J10', include:'values,formulas', tableMaxRows:4,tableMaxCols:10,maxChars:3500})).ndjson);
} else {
  const preview = await wb.render({sheetName:'Template',range:mode === 'before' ? 'A3:Q6' : 'A3:J10',scale:1.5,format:'png'});
  await fs.writeFile(`${root}/05-min-cleanup-${mode}.png`,new Uint8Array(await preview.arrayBuffer()));
  console.log(`${root}/05-min-cleanup-${mode}.png`);
}
