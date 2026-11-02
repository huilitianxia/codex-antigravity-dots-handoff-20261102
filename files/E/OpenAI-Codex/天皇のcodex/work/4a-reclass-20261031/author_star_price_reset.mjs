import fs from 'node:fs/promises';
import {FileBlob, SpreadsheetFile, Workbook} from '@oai/artifact-tool';
const root = 'E:/OpenAI-Codex/天皇のcodex/work/4a-reclass-20261031';
const source = 'D:/下载文件/PriceAndQuantity.xlsm';
const final = 'E:/OpenAI-Codex/天皇のcodex/outputs/01a18a7c-7953-7b83-b51d-1a7f216ae7e1/20261031-urgent-fixes/07-star-full-adhesive-price-reset.xlsm';
const mode = process.argv[2] || 'author';
const wb = await SpreadsheetFile.importXlsx(await FileBlob.load(mode === 'verify' ? final : source));
const sheet = wb.worksheets.getItem('Template');
const changes = {
 A7:'4A 305-Full Adhesive', K7:10.99,L7:'2026-11-01',M7:'2026-11-30',P7:9.49,U7:'Percent',V7:2,W7:3,X7:5,Y7:4,Z7:10,AA7:5,
 A8:'4A 302-Full Adhesive-400',K8:17.99,L8:'2026-11-01',M8:'2026-11-30',P8:17.56,U8:'Percent',V8:2,W8:2,X8:5,Y8:3,Z8:10,AA8:5,
};
if(mode === 'author') {
 for(const [addr,value] of Object.entries(changes)) sheet.getRange(addr).values=[[value]];
 wb.recalculate();
 await (await SpreadsheetFile.exportXlsx(wb)).save(`${root}/07-star-authored-cells.xlsx`);
 await fs.writeFile(`${root}/07-star-spec.json`,JSON.stringify({source,final,changes},null,2));
} else {
 for(const [addr,value] of Object.entries(changes)) {
  const found=sheet.getRange(addr).values[0][0];
  if(found!==value) throw new Error(`${addr}: ${found} != ${value}`);
 }
 for(const range of ['A3:M8','N3:AA8']) {
  const blob=await wb.render({sheetName:'Template',range,scale:1.2,format:'png'});
  await fs.writeFile(`${root}/07-star-${range.replace(':','-')}.png`,new Uint8Array(await blob.arrayBuffer()));
 }
 const review=Workbook.create(); const rs=review.worksheets.add('Review');
 rs.getRange('A1:H3').values=[['SKU','Sale USD','Start','End','Business USD','2 units %','5 units %','10 units %'],...['7','8'].map(r=>['A','K','L','M','P','W','Y','AA'].map(c=>sheet.getRange(c+r).values[0][0]))];
 rs.getRange('A1:H3').format.font={name:'Arial',size:11};
 rs.getRange('A1:H1').format.fill='#DDEBF7'; rs.getRange('A1:H1').format.font.bold=true;
 rs.getRange('A1:A3').format.columnWidth=34;
 rs.getRange('B1:H3').format.columnWidth=16;
 rs.getRange('A1:H3').format.rowHeight=25;
 review.recalculate();
 const rb=await review.render({sheetName:'Review',range:'A1:H3',scale:1.5,format:'png'});
 await fs.writeFile(`${root}/07-star-readable-check.png`,new Uint8Array(await rb.arrayBuffer()));
 console.log('Artifact import verified all 24 authorized cells.');
}
console.log((await wb.inspect({kind:'table',range:'Template!A7:AF8',include:'values,formulas',tableMaxRows:2,tableMaxCols:32,maxChars:4000})).ndjson);
