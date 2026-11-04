import fs from 'node:fs/promises';
import {FileBlob,SpreadsheetFile,Workbook} from '@oai/artifact-tool';
const p='E:/OpenAI-Codex/天皇のcodex/work/4a-reclass-20261031/';
const out='E:/OpenAI-Codex/天皇のcodex/outputs/01a18a7c-7953-7b83-b51d-1a7f216ae7e1/20261031-urgent-fixes/';
const plan=JSON.parse(await fs.readFile(p+'v4-receipt-repair-plan.json','utf8'));
const raw=JSON.parse(await fs.readFile(p+'category-report-raw.json','utf8'));
const rows=plan.records.filter(r=>['4A 189','4A001','4A078'].includes(r.sku));
if(process.argv.includes('--review-only')){
 const review=Workbook.create();const r=review.worksheets.add('Review');
 r.getRange('A1:G4').values=[['SKU','ASIN','Bullet 1','Bullet 2','Bullet 3','Bullet 4','Bullet 5'],...rows.map(x=>[x.sku,x.asin,...x.proposed_changes.find(z=>z.attribute==='bullet_point').draft])];
 r.getRange('A1:G4').format.columnWidth=29;r.getRange('A1:G4').format.wrapText=true;r.getRange('A1:G4').format.rowHeight=80;
 r.getRange('A1:G1').format.font.bold=true;review.recalculate();
 await fs.writeFile(p+'three-bullets-review.png',new Uint8Array(await (await review.render({sheetName:'Review',range:'A1:G4',scale:1.2,format:'png'})).arrayBuffer()));process.exit(0);
}
const source='D:/下载文件/分类商品报告_10-31-2026.xlsm';
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(source));
const sh=wb.worksheets.getItem('Template');
const preview=await wb.render({sheetName:'Template',range:'AS4:AW9',scale:1,format:'png'});
await fs.writeFile(p+'three-bullets-template-before.png',new Uint8Array(await preview.arrayBuffer()));
if(process.argv.includes('--preview-only'))process.exit(0);
sh.getRange('A7:TX1000').clear({applyTo:'contents'});
function col(i){let s='';for(i++;i;i=Math.floor((i-1)/26))s=String.fromCharCode(65+(i-1)%26)+s;return s;}
const operations=rows.map((r,i)=>{
 const cells={C:r.sku,D:'SELF_STICK_NOTE',E:'Edit (Partial Update)',L:'ASIN',M:r.asin};
 const draft=r.proposed_changes.find(c=>c.attribute==='bullet_point').draft;
 for(let n=1;n<=5;n++){
  const idx=raw.headers.findIndex(h=>h[1]===`bullet_point[marketplace_id=ATVPDKIKX0DER][language_tag=en_US]#${n}.value`);
  if(idx<0)throw new Error('Missing header');cells[col(idx)]=draft[n-1];
 }
 for(const [c,v]of Object.entries(cells))sh.getRange(c+(i+7)).values=[[v]];
 return {sku:r.sku,asin:r.asin,cells};
});
wb.recalculate();
await fs.writeFile(p+'three-bullets-operations.json',JSON.stringify(operations,null,2));
await (await SpreadsheetFile.exportXlsx(wb)).save(p+'three-bullets-cells.xlsx');
const im=await wb.render({sheetName:'Template',range:'AS4:AW9',scale:1.4,format:'png'});
await fs.writeFile(p+'three-bullets-after.png',new Uint8Array(await im.arrayBuffer()));
console.log(JSON.stringify({rows:operations.length,columns:Object.keys(operations[0].cells),out}));
