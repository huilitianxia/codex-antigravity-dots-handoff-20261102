import fs from 'node:fs/promises';
import {FileBlob, SpreadsheetFile, Workbook} from '@oai/artifact-tool';
const root='E:/OpenAI-Codex/天皇のcodex/work/4a-reclass-20261031';
const source='D:/下载文件/PriceAndQuantity.xlsm';
const final='E:/OpenAI-Codex/天皇のcodex/outputs/01a18a7c-7953-7b83-b51d-1a7f216ae7e1/20261031-urgent-fixes/09-073-business-only.xlsm';
const mode=process.argv[2]||'author';
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(mode==='verify'?final:source));
const sheet=wb.worksheets.getItem('Template');
const changes={A7:'4A073',P7:9.49,U7:'Percent',V7:3,W7:2,X7:5,Y7:3,Z7:10,AA7:5};
if(mode==='author'){
 const before=await wb.render({sheetName:'Template',range:'P3:AA7',scale:1.2,format:'png'});
 await fs.writeFile(`${root}/09-073-template-before.png`,new Uint8Array(await before.arrayBuffer()));
 for(const [a,v]of Object.entries(changes))sheet.getRange(a).values=[[v]];
 wb.recalculate();
 await(await SpreadsheetFile.exportXlsx(wb)).save(`${root}/09-073-authored-cells.xlsx`);
 await fs.writeFile(`${root}/09-073-spec.json`,JSON.stringify({source,final,changes},null,2));
}else{
 for(const [a,v]of Object.entries(changes))if(sheet.getRange(a).values[0][0]!==v)throw new Error(a);
 wb.recalculate();
 const review=Workbook.create();const rs=review.worksheets.add('Review');
 rs.getRange('A1:H2').values=[['SKU','Business USD','Qty 1','Discount %','Qty 2','Discount %','Qty 3','Discount %'],['4A073',9.49,3,2,5,3,10,5]];
 rs.getRange('A1:H2').format.font={name:'Arial',size:11};
 rs.getRange('A1:H1').format.fill='#DDEBF7';rs.getRange('A1:H1').format.font.bold=true;
 rs.getRange('A1:H2').format.columnWidth=17;rs.getRange('A1:H2').format.rowHeight=26;
 review.recalculate();
 const img=await review.render({sheetName:'Review',range:'A1:H2',scale:1.5,format:'png'});
 await fs.writeFile(`${root}/09-073-readable-check.png`,new Uint8Array(await img.arrayBuffer()));
 console.log('Verified all 9 authorized cells from final XLSM.');
}
console.log((await wb.inspect({kind:'table',range:'Template!A7:AF7',include:'values,formulas',tableMaxRows:1,tableMaxCols:32,maxChars:2500})).ndjson);
