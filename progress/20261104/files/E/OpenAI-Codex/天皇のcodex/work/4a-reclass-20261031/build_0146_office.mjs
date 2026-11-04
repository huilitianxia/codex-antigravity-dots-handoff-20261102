import fs from 'node:fs/promises';
import {FileBlob,SpreadsheetFile,Workbook} from '@oai/artifact-tool';
const p='E:/OpenAI-Codex/天皇のcodex/work/4a-reclass-20261031/';
const source='D:/下载文件/分类商品报告_10-31-2026.xlsm';
const final='E:/OpenAI-Codex/天皇のcodex/outputs/01a18a7c-7953-7b83-b51d-1a7f216ae7e1/20261031-urgent-fixes/13-0146-office-only.xlsm';
const cells={C:'4A 0146',D:'WRITING_BOARD',E:'Edit (Partial Update)',L:'ASIN',M:'B0778HMZ9W',GD:'Office'};
const before=process.argv.includes('--before'),verify=process.argv.includes('--verify');
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(verify?final:source));
const sh=wb.worksheets.getItem('Template');
if(before){
 const blob=await wb.render({sheetName:'Template',range:'GC803:GE806',scale:1.3,format:'png'});
 await fs.writeFile(p+'13-template-before.png',new Uint8Array(await blob.arrayBuffer()));
}else if(!verify){
 sh.getRange('A7:TX1200').clear({applyTo:'contents'});
 for(const[c,v]of Object.entries(cells))sh.getRange(c+'7').values=[[v]];
 wb.recalculate();
 await(await SpreadsheetFile.exportXlsx(wb)).save(p+'13-authored-cells.xlsx');
}else{
 for(const[c,v]of Object.entries(cells))if(sh.getRange(c+'7').values[0][0]!==v)throw new Error('Mismatch '+c);
 wb.recalculate();
 console.log((await wb.inspect({kind:'table',range:'Template!GD7:GH7',include:'values,formulas',tableMaxRows:1,tableMaxCols:5})).ndjson);
 const review=Workbook.create(),s=review.worksheets.add('Review');
 s.getRange('A1:F2').values=[['SKU','Product type','Action','ID type','ASIN','Recommended uses en_US'],Object.values(cells)];
 s.getRange('A1:F2').format.font={name:'Arial',size:11};s.getRange('A1:F2').format.wrapText=true;
 s.getRange('A:F').format.columnWidth=24;s.getRange('A1:F2').format.rowHeight=36;s.getRange('A1:F1').format.fill='#DDEBF7';
 review.recalculate();
 await fs.writeFile(p+'13-readable-check.png',new Uint8Array(await(await review.render({sheetName:'Review',range:'A1:F2',scale:1.3,format:'png'})).arrayBuffer()));
 console.log(JSON.stringify({verified:6,cells,final}));
}
