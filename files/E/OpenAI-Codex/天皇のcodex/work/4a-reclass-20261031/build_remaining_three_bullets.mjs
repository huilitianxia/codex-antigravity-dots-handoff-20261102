import fs from 'node:fs/promises';
import {FileBlob,SpreadsheetFile,Workbook}from'@oai/artifact-tool';
const p='E:/OpenAI-Codex/天皇のcodex/work/4a-reclass-20261031/';
const final='E:/OpenAI-Codex/天皇のcodex/outputs/01a18a7c-7953-7b83-b51d-1a7f216ae7e1/20261031-urgent-fixes/11-remaining-three-five-bullets-only.xlsm';
const source='D:/下载文件/分类商品报告_10-31-2026.xlsm';
const sourceRows=JSON.parse(await fs.readFile(p+'six-bullet-factual-review.json','utf8'));
const rows=sourceRows.filter(r=>['4A 404SL-15','4A 406SL-10','4A 6032x5'].includes(r.sku));
if(rows.length!==3)throw new Error('Expected exactly three reviewed rows');
const ops=rows.map(r=>({sku:r.sku,asin:r.asin,cells:{C:r.sku,D:'SELF_STICK_NOTE',E:'Edit (Partial Update)',L:'ASIN',M:r.asin,...r.proposed_bullets}}));
const verify=process.argv.includes('--verify');
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(verify?final:source));
const sh=wb.worksheets.getItem('Template');
if(!verify){
 const preview=await wb.render({sheetName:'Template',range:'AS4:AW9',scale:1,format:'png'});
 await fs.writeFile(p+'11-template-before.png',new Uint8Array(await preview.arrayBuffer()));
 sh.getRange('A7:TX1000').clear({applyTo:'contents'});
 for(const[i,op]of ops.entries())for(const[c,v]of Object.entries(op.cells))sh.getRange(c+(i+7)).values=[[v]];
 wb.recalculate();
 await(await SpreadsheetFile.exportXlsx(wb)).save(p+'11-authored-cells.xlsx');
 await fs.writeFile(p+'11-operations.json',JSON.stringify(ops,null,2));
}else{
 for(const[i,op]of ops.entries())for(const[c,v]of Object.entries(op.cells))if(sh.getRange(c+(i+7)).values[0][0]!==v)throw new Error('Mismatch '+c+(i+7));
 wb.recalculate();
 const review=Workbook.create();const s=review.worksheets.add('Review');
 s.getRange('A1:G4').values=[['SKU','ASIN','Bullet 1','Bullet 2','Bullet 3','Bullet 4','Bullet 5'],...rows.map(r=>[r.sku,r.asin,...Object.values(r.proposed_bullets)])];
 s.getRange('A1:G4').format.columnWidth=28;s.getRange('A1:G4').format.wrapText=true;s.getRange('A1:G4').format.rowHeight=110;
 s.getRange('A1:G4').format.font={name:'Arial',size:11};s.getRange('A1:G1').format.rowHeight=26;s.getRange('A1:G1').format.font.bold=true;s.getRange('A1:G1').format.fill='#DDEBF7';
 review.recalculate();
 await fs.writeFile(p+'11-readable-check.png',new Uint8Array(await(await review.render({sheetName:'Review',range:'A1:G4',scale:1.2,format:'png'})).arrayBuffer()));
 console.log('Final XLSM reimport verified30 authorized cells,15 bullets.');
}
console.log(JSON.stringify({rows:ops.length,identities:ops.map(x=>[x.sku,x.asin]),columns:Object.keys(ops[0].cells),final}));
