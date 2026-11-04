import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {FileBlob,Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const base=path.dirname(fileURLToPath(import.meta.url));
const plan=JSON.parse(await fs.readFile(path.join(base,'validated-price-upload-plan.json'),'utf8'));
const source=path.join(base,'Official-PriceAndQuantity-20261103.xlsm');
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(source));
const s=wb.worksheets.getItem('Template');
const rows=plan.rows.map(r=>{
 const a=Array(32).fill(null);
 a[0]=r.sku;
 a[6]=r.new_price;a[8]=r.floor;a[10]=r.new_sale;
 a[11]=r.sale_start;a[12]=r.sale_end;
 a[15]=r.business;a[16]=r.floor;a[20]='Fixed';
 for(let i=0;i<r.tiers.length;i++){a[21+2*i]=r.tiers[i].qty;a[22+2*i]=r.tiers[i].price;}
 if(r.fulfillment==='FBM')a[31]=r.shipping_template;
 return a;
});
if(rows.length!==7||new Set(rows.map(r=>r[0])).size!==7)throw Error('Expected7uniqueSKUs');
s.getRange('A7:AF13').values=rows;
for(const c of ['G','I','K','P','Q','W','Y','AA'])s.getRange(`${c}7:${c}13`).setNumberFormat('0.00');
s.getRange('A7:AF13').format.rowHeight=22;
wb.recalculate();
const check=await wb.inspect({kind:'region',sheetId:'Template',range:'A7:M13',maxChars:2200,tableMaxRows:7,tableMaxCols:13});
await fs.writeFile(path.join(base,'official-upload-inspection.ndjson'),check.ndjson);
const out=path.resolve(base,'../../outputs/01a18a7c-7953-7b83-b51d-1a7f216ae7e1/20261103-price-upload');
await fs.mkdir(out,{recursive:true});
const filename=path.join(out,'正式上传_美国站_已核验7SKU价格更新_20261103.xlsx');
await(await SpreadsheetFile.exportXlsx(wb)).save(filename);
for(const [range,file]of [['A4:M13','official-upload-retail-preview.png'],['P4:AF13','official-upload-business-preview.png']]){
 const img=await wb.render({sheetName:'Template',range,scale:1,format:'png'});
 await fs.writeFile(path.join(base,file),new Uint8Array(await img.arrayBuffer()));
}
await fs.writeFile(path.join(base,'official-upload-output.json'),JSON.stringify({filename,source,rows:7,firstDataRow:7,lastDataRow:13,columns:32},null,2));
console.log(JSON.stringify({filename,rows:rows.length}));
