import fs from 'node:fs/promises';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load('E:/Desktop/4A_库存分类与合并复核_20261031.xlsx'));
const blob=await wb.render({sheetName:'经营总览',range:'A17:C22',scale:1,format:'png'});
await fs.writeFile('E:/OpenAI-Codex/天皇のcodex/work/4a-reclass-20261031/preview_final_metrics.png',new Uint8Array(await blob.arrayBuffer()));
console.log('Final metric view rendered');
