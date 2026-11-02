import fs from 'node:fs/promises';
import {FileBlob,SpreadsheetFile,Workbook} from '@oai/artifact-tool';
const root='E:/OpenAI-Codex/天皇のcodex/work/4a-reclass-20261031';
const source='D:/下载文件/PriceAndQuantity.xlsm';
const final='E:/OpenAI-Codex/天皇のcodex/outputs/01a18a7c-7953-7b83-b51d-1a7f216ae7e1/20261031-urgent-fixes/10-four-noncoupon-promotions.xlsm';
const rows=[
 ['AAAA 4A PSS 9-1 NGGrid',17.99,17.49],
 ['4A 004',14.39,13.99],
 ['AAAA 4A 301x12-N',15.29,14.99],
 ['4A 301x24x2',23.39,22.99],
];
const changes={};
for(let i=0;i<rows.length;i++){
 const r=i+7;const[sku,sale,business]=rows[i];
 Object.assign(changes,{[`A${r}`]:sku,[`K${r}`]:sale,[`L${r}`]:'2026-11-02',[`M${r}`]:'2026-11-16',[`P${r}`]:business,[`U${r}`]:'Percent',[`V${r}`]:3,[`W${r}`]:2,[`X${r}`]:5,[`Y${r}`]:3,[`Z${r}`]:10,[`AA${r}`]:5});
}
const mode=process.argv[2]||'author';
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(mode==='verify'?final:source));
const sheet=wb.worksheets.getItem('Template');
if(mode==='author'){
 const before=await wb.render({sheetName:'Template',range:'K3:AA7',scale:1.2,format:'png'});
 await fs.writeFile(`${root}/10-four-template-before.png`,new Uint8Array(await before.arrayBuffer()));
 for(const[a,v]of Object.entries(changes))sheet.getRange(a).values=[[v]];
 wb.recalculate();
 await(await SpreadsheetFile.exportXlsx(wb)).save(`${root}/10-four-authored-cells.xlsx`);
 await fs.writeFile(`${root}/10-four-spec.json`,JSON.stringify({source,final,changes,rows,requested_active_dates:'2026-11-02 through 2026-11-15 inclusive',sale_end_at:'2026-11-16 00:00 per official template Data Definitions D17',business_tiers_persist_after_sale_end:true},null,2));
}else{
 for(const[a,v]of Object.entries(changes))if(sheet.getRange(a).values[0][0]!==v)throw new Error(a);
 wb.recalculate();
 const review=Workbook.create();const rs=review.worksheets.add('Review');
 rs.getRange('A1:H5').values=[['SKU','Sale USD','Start','End at 00:00','Business USD','3 units %','5 units %','10 units %'],...rows.map(([sku,sale,business])=>[sku,sale,'2026-11-02','2026-11-16',business,2,3,5])];
 rs.getRange('A1:H5').format.font={name:'Arial',size:11};
 rs.getRange('A1:H1').format.fill='#DDEBF7';rs.getRange('A1:H1').format.font.bold=true;
 rs.getRange('A1:A5').format.columnWidth=32;rs.getRange('B1:H5').format.columnWidth=17;
 rs.getRange('A1:H5').format.rowHeight=26;
 review.recalculate();
 const img=await review.render({sheetName:'Review',range:'A1:H5',scale:1.5,format:'png'});
 await fs.writeFile(`${root}/10-four-readable-check.png`,new Uint8Array(await img.arrayBuffer()));
 console.log('Verified all48 authorized cells from final XLSM.');
}
console.log((await wb.inspect({kind:'table',range:'Template!A7:AF10',include:'values,formulas',tableMaxRows:4,tableMaxCols:32,maxChars:3000})).ndjson);
