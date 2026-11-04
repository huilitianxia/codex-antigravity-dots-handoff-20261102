import fs from 'node:fs/promises';
import {Workbook,FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const root='E:/OpenAI-Codex/天皇のcodex/work/4a-reclass-20261031';
const consolidated=process.argv.includes('--consolidated');
const execution=process.argv.includes('--execution');
const safeExecution=process.argv.includes('--safe-execution');
const data=JSON.parse(await fs.readFile(root+(safeExecution?'/safe-v4-data.json':execution?'/execution-batch-data.json':consolidated?'/consolidated-repairs-data.json':'/urgent-batches-data.json'),'utf8'));
const specs=safeExecution?[
 {key:'operations',stem:'04-reviewed-nonincident-fixes',source:'D:/下载文件/分类商品报告_10-31-2026.xlsm',range:'C4:M10'}
]:execution?[
 {key:'operations',stem:'04-clearance-business-copy-fixes',source:'D:/下载文件/分类商品报告_10-31-2026.xlsm',range:'C4:M10'}
]:consolidated?[
 {key:'operations',stem:'03-catalog-errors-consolidated',source:'D:/下载文件/分类商品报告_10-31-2026.xlsm',range:'C4:M10'}
]:[
 {key:'price_updates',stem:'01-price-title-fixes',source:'D:/下载文件/分类商品报告_10-31-2026.xlsm',range:'C4:M10'},
 {key:'restore',stem:'02-restore-original-skus',source:'D:/下载文件/restore-batch-01-New_Version.xlsm',range:'A4:F10'}
];
if(process.argv.includes('--verify')){
 const output='E:/OpenAI-Codex/天皇のcodex/outputs/01a18a7c-7953-7b83-b51d-1a7f216ae7e1/20261031-urgent-fixes';
 for(const x of specs){
  const w=await SpreadsheetFile.importXlsx(await FileBlob.load(output+'/'+x.stem+'.xlsm'));
  if(consolidated) console.log('imported value sample',JSON.stringify(w.worksheets.getItem('Template').getRange('C7:J8').values));
  const ranges=safeExecution?['C4:E14','AS4:AW14','MJ4:ND10']:execution?['C4:E14','MJ4:MP14','MS4:ND14','AS4:AW14']:consolidated?['C4:E14','I4:J14','BG4:BH14','I75:J85','I160:J170']:x.key==='price_updates'?['C4:E12','MJ4:MN12','MS4:NB12','I110:J112']:['A4:B15','AL4:AQ15','CF4:CF15','DC4:DC15'];
  for(const [i,range] of ranges.entries()){
   const b=await w.render({sheetName:'Template',range,scale:1.2,format:'png'});
   await fs.writeFile(root+'/'+x.stem+'-after-'+i+'.png',new Uint8Array(await b.arrayBuffer()));
  }
  if(safeExecution){
   const actual=w.worksheets.getItem('Template');
   for(const [i,r] of data.operations.entries())for(const [c,v] of Object.entries(r.cells)){
    const got=actual.getRange(c+(i+7)).values[0][0];
    if(got!==v)throw new Error('Saved import mismatch '+c+(i+7));
   }
   const qa=Workbook.create(),qs=qa.worksheets.add('Copy review');
   const rows=data.operations.filter(r=>r.cells.AW);
   qs.getRange('A1').write([['SKU','ASIN','Bullet 1','Bullet 5'],...rows.map(r=>[r.sku,r.asin,r.cells.AS??'(unchanged)',r.cells.AW])]);
   qs.getRange('A1:D'+(rows.length+1)).format.font={name:'Arial',size:11,color:'#17243A'};
   qs.getRange('A1:D'+(rows.length+1)).format.wrapText=true;
   qs.getRange('A1:D'+(rows.length+1)).format.rowHeight=64;
   for(const [c,width]of [['A',34],['B',18],['C',55],['D',70]])qs.getRange(c+'1:'+c+(rows.length+1)).format.columnWidth=width;
   qs.getRange('A1:D1').format.fill='#243B5A';qs.getRange('A1:D1').format.font.color='#FFFFFF';
   qa.recalculate();
   for(const [i,range]of ['A1:D12',`A${Math.max(1,rows.length-10)}:D${rows.length+1}`].entries()){
    const b=await qa.render({sheetName:'Copy review',range,scale:1,format:'png'});
    await fs.writeFile(root+'/'+x.stem+'-copy-review-'+i+'.png',new Uint8Array(await b.arrayBuffer()));
   }
   if(data.pricing.length){
    const ps=qa.worksheets.add('Price review');
    const prices=data.pricing.map(p=>{
     const ix=data.operations.findIndex(r=>r.sku===p.sku)+7;
     return [p.sku,p.asin,...['MJ','MN','MO','MP','MS'].map(c=>actual.getRange(c+ix).values[0][0])];
    });
    ps.getRange('A1').write([['SKU','ASIN','Regular change','Sale price','Start date','End date','Business change'],...prices]);
    ps.getRange('A1:G'+(prices.length+1)).format.font={name:'Arial',size:11,color:'#17243A'};
    ps.getRange('A1:G'+(prices.length+1)).format.wrapText=true;
    ps.getRange('A1:G'+(prices.length+1)).format.rowHeight=44;
    ps.getRange('A1:A'+(prices.length+1)).format.columnWidth=34;
    ps.getRange('B1:G'+(prices.length+1)).format.columnWidth=19;
    ps.getRange('A1:G1').format.fill='#243B5A';ps.getRange('A1:G1').format.font.color='#FFFFFF';
    qa.recalculate();
    const b=await qa.render({sheetName:'Price review',range:'A1:G'+(prices.length+1),scale:1,format:'png'});
    await fs.writeFile(root+'/'+x.stem+'-price-review.png',new Uint8Array(await b.arrayBuffer()));
   }
   console.log('safeV4 artifact import values verified',data.operations.length);
  }
  if(execution){
   const actual=w.worksheets.getItem('Template');
   for(const [i,r] of data.operations.entries())for(const [c,v] of Object.entries(r.cells)){
    const got=actual.getRange(c+(i+7)).values[0][0];
    if(got!==v)throw new Error('Imported value mismatch '+c+(i+7)+' '+got+' != '+v);
   }
   const qa=Workbook.create(),qs=qa.worksheets.add('Price verification');
   const values=[['SKU','Regular','Sale before','Sale new','B2B new','Qty discounts','FBA fee','Minimum cash'],...data.pricing.map(r=>[r.sku,r.regular,r.sale_before,r.sale_new??r.regular_new,r.business_new,r.tiers.map(t=>t[0]+'+ / '+t[1]+'%').join('; '),r.fba_fee,r.minimum_cash])];
   qs.getRange('A1').write(values);
   const last=values.length;
   qs.getRange('A1:H'+last).format.font={name:'Arial',size:11,color:'#17243A'};
   qs.getRange('A1:H'+last).format.wrapText=true;
   qs.getRange('A1:H'+last).format.rowHeight=38;
   for(const [c,width]of [['A',34],['B',12],['C',12],['D',12],['E',12],['F',31],['G',12],['H',14]])qs.getRange(c+'1:'+c+last).format.columnWidth=width;
   qs.getRange('A1:H1').format.fill='#243B5A';qs.getRange('A1:H1').format.font.color='#FFFFFF';
   const cs=qa.worksheets.add('Bullet verification');
   const bulletOps=data.operations.filter(r=>'AS'in r.cells);
   cs.getRange('A1').write([['SKU','Bullet 1','Bullet 2','Bullet 3','Bullet 4','Bullet 5'],...bulletOps.map(r=>[r.sku,...['AS','AT','AU','AV','AW'].map(c=>r.cells[c])])]);
   cs.getRange('A1:F7').format.font={name:'Arial',size:11,color:'#17243A'};
   cs.getRange('A1:F7').format.wrapText=true;cs.getRange('A1:F7').format.rowHeight=116;
   cs.getRange('A1:F7').format.columnWidth=28;cs.getRange('A1:F1').format.rowHeight=28;
   cs.getRange('A1:F1').format.fill='#243B5A';cs.getRange('A1:F1').format.font.color='#FFFFFF';
   qa.recalculate();
   for(const [i,range] of ['A1:H16','A16:H30'].entries()){
    const b=await qa.render({sheetName:qs.name,range,scale:1,format:'png'});
    await fs.writeFile(root+'/'+x.stem+'-prices-'+i+'.png',new Uint8Array(await b.arrayBuffer()));
   }
   const b=await qa.render({sheetName:cs.name,range:'A1:F7',scale:1,format:'png'});
   await fs.writeFile(root+'/'+x.stem+'-bullets.png',new Uint8Array(await b.arrayBuffer()));
   console.log('Execution import cells verified',data.operations.length);
  }
  if(consolidated){
   const imported=w.worksheets.getItem('Template').getRange('C7:BG170').values;
   const qa=Workbook.create(),qs=qa.worksheets.add('Content verification');
   const values=[['SKU','Item Name','Item Highlight','Color','Manufacturer'],...imported.map(r=>[r[0],r[6],r[7],r[56],r[17]])];
   qs.getRange('A1').write(values);
   qs.getRange('A1:E165').format.font={name:'Arial',size:11,color:'#17243A'};
   qs.getRange('A1:E165').format.wrapText=true;
   qs.getRange('A1:E165').format.rowHeight=42;
   for(const [c,width] of [['A',32],['B',65],['C',53],['D',29],['E',29]])qs.getRange(c+'1:'+c+'165').format.columnWidth=width;
   qs.getRange('A1:E1').format.fill='#243B5A';qs.getRange('A1:E1').format.font.color='#FFFFFF';
   qa.recalculate();
   for(const [i,range] of ['A1:E12','A75:E86','A154:E165'].entries()){
    const b=await qa.render({sheetName:qs.name,range,scale:1,format:'png'});
    await fs.writeFile(root+'/'+x.stem+'-content-'+i+'.png',new Uint8Array(await b.arrayBuffer()));
   }
  }
  console.log('verified render',x.stem);
 }
}else if(process.argv.includes('--before')){
 for(const x of specs){
  const w=await SpreadsheetFile.importXlsx(await FileBlob.load(x.source));
  const b=await w.render({sheetName:'Template',range:x.range,scale:1,format:'png'});
  await fs.writeFile(root+'/'+x.stem+'-before.png',new Uint8Array(await b.arrayBuffer()));
  console.log('rendered source',x.stem);
 }
}else{
 for(const x of specs){
  const w=Workbook.create(),s=w.worksheets.add('Template');
  for(const [i,r] of data[x.key].entries())for(const [c,v] of Object.entries(r.cells))s.getRange(c+(i+7)).values=[[v]];
  w.recalculate();
  const out=await SpreadsheetFile.exportXlsx(w);await out.save(root+'/'+x.stem+'-cells.xlsx');
  console.log('authored',x.stem,data[x.key].length);
 }
}
