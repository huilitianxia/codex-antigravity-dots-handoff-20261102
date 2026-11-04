import fs from 'node:fs/promises';
import { FileBlob, SpreadsheetFile } from '@oai/artifact-tool';
const root='E:/OpenAI-Codex/天皇のcodex/work/4a-reclass-20261031';
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load('D:/下载文件/restore-batch-01-New_Version.xlsm'));
const sh=wb.worksheets.getItem('Template');
if(process.argv.includes('--edit')){
  sh.getRange('CF7:CF13').values=[['No']];
  sh.getRange('DC7:DC13').values=[['Not Applicable']];
  wb.recalculate();
  console.log(JSON.stringify({battery:sh.getRange('CF7:CF13').values,hazmat:sh.getRange('DC7:DC13').values}));
  const x=await SpreadsheetFile.exportXlsx(wb);await x.save(root+'/restore-batch-01-cells.xlsx');
}
const stage=process.argv.includes('--edit')?'after':'before';
for(const [name,range] of [['battery','CE4:CG13'],['hazmat','DC4:DE13']]){
  const p=await wb.render({sheetName:'Template',range,scale:1.4,format:'png'});
  await fs.writeFile(root+`/restore-${name}-${stage}.png`,new Uint8Array(await p.arrayBuffer()));
}
