import fs from 'node:fs/promises';
import {FileBlob,SpreadsheetFile,Workbook} from '@oai/artifact-tool';
const p='E:/OpenAI-Codex/天皇のcodex/work/4a-reclass-20261031/';
const source='D:/下载文件/分类商品报告_10-31-2026.xlsm';
const final='E:/OpenAI-Codex/天皇のcodex/outputs/01a18a7c-7953-7b83-b51d-1a7f216ae7e1/20261031-urgent-fixes/12-catalog-text-repairs-only.xlsm';
const data=JSON.parse(await fs.readFile(p+'12-text-operations-draft.json','utf8'));
const ops=data.operations;
const verify=process.argv.includes('--verify');
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(verify?final:source));
const sh=wb.worksheets.getItem('Template');
const allow=new Set(['C','D','E','I','J','L','M','AR','AS','AT','AU','AV','AW']);
for(const op of ops){
 for(const c of Object.keys(op.cells))if(!allow.has(c))throw new Error('Unexpected column '+c);
 if(op.cells.I&&op.cells.I.length>75)throw new Error('Title too long '+op.sku);
 if(op.cells.J&&op.cells.J.length>125)throw new Error('Highlight too long '+op.sku);
 if(op.cells.J&&/^B[A-Z0-9]{9}$/.test(op.cells.J))throw new Error('ASIN highlight '+op.sku);
}
if(!verify){
 sh.getRange('A7:TX1200').clear({applyTo:'contents'});
 for(const [i,op]of ops.entries())for(const[c,v]of Object.entries(op.cells))sh.getRange(c+(i+7)).values=[[v]];
 wb.recalculate();
 const inspect=await wb.inspect({kind:'table',range:'Template!I7:J12',include:'values,formulas',tableMaxRows:6,tableMaxCols:2,maxChars:2200});
 console.log(inspect.ndjson);
 await(await SpreadsheetFile.exportXlsx(wb)).save(p+'12-authored-cells.xlsx');
}else{
 let count=0;
 for(const [i,op]of ops.entries())for(const[c,v]of Object.entries(op.cells)){
  if(sh.getRange(c+(i+7)).values[0][0]!==v)throw new Error('Saved mismatch '+c+(i+7));count++;
 }
 wb.recalculate();
 const review=Workbook.create();
 const s=review.worksheets.add('Titles');
 const samples=['4A 6032','4A Meeting-51','4A 008','4A 303-Holder+Flag','4A BP1515 NGORY','4A 60144x2'];
 const chosen=samples.map(x=>ops.find(o=>o.sku===x)).filter(Boolean);
 s.getRange(`A1:D${chosen.length+1}`).values=[['SKU','Previous title','Item name','Item highlights'],...chosen.map(o=>[o.sku,Object.entries(o.before).find(([k])=>k.startsWith('item_name'))?.[1]||'',o.cells.I,o.cells.J])];
 s.getRange(`A1:D${chosen.length+1}`).format.font={name:'Arial',size:11};
 s.getRange(`A1:D${chosen.length+1}`).format.wrapText=true;
 s.getRange('A:A').format.columnWidth=25;s.getRange('B:B').format.columnWidth=60;s.getRange('C:D').format.columnWidth=48;
 s.getRange(`A2:D${chosen.length+1}`).format.rowHeight=108;s.getRange('A1:D1').format.rowHeight=26;
 s.getRange('A1:D1').format.fill='#DDEBF7';s.getRange('A1:D1').format.font.bold=true;
 const c=review.worksheets.add('Copy');
 const cchosen=ops.filter(o=>o.cells.AR&&o.cells.AV).slice(0,4);
 c.getRange(`A1:C${cchosen.length+1}`).values=[['SKU','Description','Bullet 4'],...cchosen.map(o=>[o.sku,o.cells.AR,o.cells.AV])];
 c.getRange(`A1:C${cchosen.length+1}`).format.font={name:'Arial',size:11};c.getRange(`A1:C${cchosen.length+1}`).format.wrapText=true;
 c.getRange('A:A').format.columnWidth=25;c.getRange('B:B').format.columnWidth=100;c.getRange('C:C').format.columnWidth=60;
 c.getRange(`A2:C${cchosen.length+1}`).format.rowHeight=120;c.getRange('A1:C1').format.rowHeight=26;c.getRange('A1:C1').format.fill='#DDEBF7';c.getRange('A1:C1').format.font.bold=true;
 review.recalculate();
 for(const [sheetName,range,file]of [['Titles',`A1:D${chosen.length+1}`,'12-title-review.png'],['Copy',`A1:C${cchosen.length+1}`,'12-copy-review.png']]){
  await fs.writeFile(p+file,new Uint8Array(await(await review.render({sheetName,range,scale:1.3,format:'png'})).arrayBuffer()));
 }
 console.log(JSON.stringify({rows:ops.length,verifiedCells:count,final}));
}
