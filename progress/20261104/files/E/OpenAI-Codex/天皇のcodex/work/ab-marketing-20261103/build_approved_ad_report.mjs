import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';

const base = path.dirname(fileURLToPath(import.meta.url));
const read = async name => JSON.parse(await fs.readFile(path.join(base, name), 'utf8'));
const attempts = await read('approved-ad-execution-20261103.json');
const added = attempts.filter(r => r.status === 'launched');
if (added.some(r => !r.independently_verified)) throw new Error('New campaign verification remains incomplete');
const morning = [...await read('precision-ad-execution.json'), ...await read('precision-ad-supplement-354818.json')].map(r=>({
  ...r, keywords:r.keywords || r.verification?.dom_targets?.rows.map(x=>x.cells.target.split('\n')[0])
}));
if(morning.some(r=>!r.keywords?.length))throw new Error('Missing morning keyword evidence');
const old = (await read('ad-cleanup-20261103/campaign-cleanup-plan.json')).campaigns.filter(r => r.decision === 'retain-old-effective6');
const hp = await read('hp10-evidence/controlled-price-test.json');
const names = {
  B01LVTWP7Q:'1 / 301×12-N', B07JVSYNYV:'2 / BS 1801', B01M3N310M:'3 / 4012',
  B01LVXOCU2:'6 / 301×24', B07RP9MB7Y:'7 / 5088-N-L', B07F2B49BL:'8 / 5084-N-L',
  B01N9HHKRM:'9 / 301×24-Y，24本单包',
  B07R1XLCP4:'13 / BP1515-N×4', B073VPHSJ9:'14 / 608SL×4', B08CVLH794:'16 / PSS32×6',
  B07B8RBCKT:'18 / 608-N-L-210', B07DJKDB63:'20 / 354818', B07Z2555TN:'404亚克力笔筒便签盒',
  B07DJXC4PJ:'2028-N，2×2便签8本', B0F2TKL2P5:'302满胶400，有效词重建', B07QXJYTZ7:'303满胶400，有效词重建',
  B07F2BHFJH:'5082-Y-L', B00SMEFFRE:'304 Full Glue', B01NGWHSK1:'303×18-Y',
  B07FK7PBHJ:'PSS9-1', B07FKG29KB:'30315', B00SMEEVCO:'5059气泡便签',
  B01M986R0Y:'6043标签', B07RQ7JMV9:'30132', B082WMV9NQ:'会议便签52张',
  B01MXYQPE1:'404×6-N', B07RP9LR73:'354832', B00SMEDUWQ:'10 / SMC434'
};
const dateFromDisplay = text => {
  const m = String(text || '').match(/(20\d{2})年(\d{1,2})月(\d{1,2})日/);
  return m ? new Date(Date.UTC(+m[1], +m[2]-1, +m[3])) : null;
};
const active = [
  ...added.sort((a,b) => Number(names[a.asin]?.match(/^(\d+)\s*\//)?.[1] || 999) - Number(names[b.asin]?.match(/^(\d+)\s*\//)?.[1] || 999)).map(r => ({
    source:'本轮新增', product:names[r.asin] || r.code, asin:r.asin, status:'已启动，独立核验通过',
    daily:r.daily, end:dateFromDisplay(r.verification.end), skus:r.skus.join('\n'),
    targeting:`${r.keywords.length}个精准词；$${Number(r.bid).toFixed(2)}；动态仅降低`, id:r.campaignId,
    keywords:r.keywords, bid:r.bid, name:r.name
  })),
  ...morning.map(r => ({
    source:'保留早上新增', product:names[r.asin] || r.code, asin:r.asin,
    status:r.asin === 'B01M3N310M' ? '保留既有；High Price等回执' : '本轮保留，未改设置', daily:r.daily,
    end:dateFromDisplay(r.verification?.end) || new Date('2026-11-09T00:00:00Z'), skus:r.skus.join('\n'),
    targeting:`${r.keywords.length}个精准词；$${Number(r.bid).toFixed(2)}；动态仅降低`, id:r.campaignId,
    keywords:r.keywords, bid:r.bid, name:r.name
  })),
  ...old.map(r => ({
    source:'保留有效旧活动', product:r.name.replace(/^SP_/,'').replace(/_20\d{6}$/,''),
    asin:r.enabled_asins.join('\n'), status:'按审定结果保留，未改设置', daily:r.daily_budget,
    end:r.end_date ? new Date(`${String(r.end_date).slice(0,4)}-${String(r.end_date).slice(4,6)}-${String(r.end_date).slice(6,8)}T00:00:00Z`) : null,
    skus:r.enabled_skus.join('\n'), targeting:r.target_summary, id:r.id, keywords:[], bid:null, name:r.name
  }))
];
const holds = [
  ['待办','3 / 4012','B01M3N310M','等待既有High Price回执',null,null,'4A 4012-B07T-FBM','既有广告保留；不新增活动。Case 22957468581。',''],
  ['不投','4 / 406×6','B01MDJCWVH','按用户审定不投',null,null,'','本轮不建广告。',''],
  ['不投','5 / BP1111-P×4','B07T55RL97','按用户审定不投',null,null,'','本轮不建广告。',''],
  ...(!added.some(r=>r.asin==='B01N9HHKRM') ? [['待办','9 / 301×24-Y','B01N9HHKRM','误选整箱广告已暂停',null,null,'4A 301x24-Y / 4A 003','用户确认24本组成一包；SC目录却混入48包整箱。需先修复单包身份与可售报价，再投放。','A02428392J4FK7WOMDKK']] : []),
  ...(!added.some(r=>r.asin==='B00SMEDUWQ') ? [['待办','10 / SMC434','B00SMEDUWQ',hp.high_price_resolved ? 'High Price已解除，待投放' : '编辑价已保存，发布与重评待核',null,null,'4A092',`编辑页售价和下限$${hp.saved_price.toFixed(2)}已回读；买家页仍$11.99+$8.99。High Price未解除，库存6。`,'']] : [])
];
const rows = active.map(r=>[r.source,r.product,r.asin,r.status,r.daily,r.end,r.skus,r.targeting,r.id]);
const keywordRows = active.flatMap(r => r.keywords.map(k=>[r.source,r.product,r.asin,k,'精准',r.bid]));
const wb = Workbook.create();
const s = wb.worksheets.add('执行结果');
const k = wb.worksheets.add('精准关键词');
s.showGridLines = false; k.showGridLines = false; s.tabColor='#234766';
s.getRange('A2').values=[['4A 广告确认范围与执行结果']];
s.getRange('A2').format.font={name:'Arial',size:14,bold:true};
const first=11,last=first+rows.length-1;
s.getRange('A4:A7').values=[['本轮新增'],['早上新增保留'],['有效旧活动保留'],['活动合计']];
s.getRange('B4').formulas=[[`=COUNTIF(A${first}:A${last},"本轮新增")`]];
s.getRange('B5').formulas=[[`=COUNTIF(A${first}:A${last},"保留早上新增")`]];
s.getRange('B6').formulas=[[`=COUNTIF(A${first}:A${last},"保留有效旧活动")`]];
s.getRange('B7').formulas=[['=SUM(B4:B6)']];
s.getRange('D4:D6').values=[['配置日预算（USD）'],['本轮新增日预算（USD）'],['精准关键词总数']];
s.getRange('E4').formulas=[[`=SUM(E${first}:E${last})`]];
s.getRange('E5').formulas=[[`=SUMIF(A${first}:A${last},"本轮新增",E${first}:E${last})`]];
s.getRange('E6').formulas=[[`=COUNTA('精准关键词'!D2:D${keywordRows.length+1})`]];
s.getRange('E4:E5').setNumberFormat('$0.00');
s.getRange('A4:E7').format.font={name:'Arial',size:10};
s.getRange('B4:B7').format.font={name:'Arial',size:10,bold:true};
s.getRange('E4:E6').format.font={name:'Arial',size:10,bold:true};
s.getRange('A8').values=[['截至2026-11-03；预算为配置值，不是实际花费。本轮新活动截止日期按广告后台实际保存值列示。']];
s.getRange('A9').values=[['来源：Amazon Ads启动回执及逐条独立回读；早上13条和6条有效旧活动按审定结果保留。']];
s.getRange('A8:A9').format.font={name:'Arial',size:9,color:'#595959'};
const headers=['范围','商品 / VC金额名次','ASIN','执行结果','日预算（USD）','截止日期','广告SKU','投放范围','活动编号'];
s.getRange(`A10:I${last}`).values=[headers,...rows];
s.getRange(`A10:I${last}`).format.font={name:'Arial',size:10};
s.getRange(`A10:I${last}`).format.verticalAlignment='center';
s.getRange(`A${first}:I${last}`).format.rowHeight=44;
for(const col of ['A','B','C','D','G','H'])s.getRange(`${col}${first}:${col}${last}`).format.wrapText=true;
s.getRange(`E${first}:E${last}`).setNumberFormat('$0.00');
s.getRange(`F${first}:F${last}`).setNumberFormat('yyyy-mm-dd');
for(const [c,w]of [['A',21],['B',29],['C',21],['D',34],['E',17],['F',17],['G',44],['H',60],['I',29]])s.getRange(`${c}1:${c}${last+holds.length+6}`).format.columnWidth=w;
s.tables.add(`A10:I${last}`,true,'ApprovedCampaigns');
s.getRange('A10:I10').format={fill:'#234766',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},horizontalAlignment:'center',verticalAlignment:'center',wrapText:true,rowHeight:32};
const holdTitle=last+3, holdHeader=holdTitle+2, holdFirst=holdHeader+1,holdLast=holdHeader+holds.length;
s.getRange(`A${holdTitle}`).values=[['不投与待办事项']];s.getRange(`A${holdTitle}`).format.font={name:'Arial',size:12,bold:true};
s.getRange(`A${holdHeader}:I${holdLast}`).values=[headers,...holds];
s.getRange(`A${holdHeader}:I${holdLast}`).format.font={name:'Arial',size:10};
s.getRange(`A${holdFirst}:I${holdLast}`).format.rowHeight=50;
s.getRange(`A${holdFirst}:I${holdLast}`).format.wrapText=true;
s.getRange(`A${holdFirst}:I${holdLast}`).format.verticalAlignment='center';
s.tables.add(`A${holdHeader}:I${holdLast}`,true,'HoldsAndExclusions');
s.getRange(`A${holdHeader}:I${holdHeader}`).format={fill:'#234766',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},horizontalAlignment:'center',verticalAlignment:'center',wrapText:true,rowHeight:32};
s.getRange(`D${holdFirst}:D${holdLast}`).conditionalFormats.add('containsText',{text:'等待',format:{fill:'#FFF2CC',font:{color:'#7F6000'}}});
s.freezePanes.freezeRows(10);s.freezePanes.freezeColumns(3);

k.getRange(`A1:F${keywordRows.length+1}`).values=[['范围','商品','ASIN','关键词','匹配','点击出价（USD）'],...keywordRows];
k.getRange(`A1:F${keywordRows.length+1}`).format.font={name:'Arial',size:10};
k.getRange(`A2:F${keywordRows.length+1}`).format.rowHeight=25;
for(const[c,w]of [['A',22],['B',30],['C',21],['D',66],['E',12],['F',20]])k.getRange(`${c}1:${c}${keywordRows.length+1}`).format.columnWidth=w;
k.getRange(`F2:F${keywordRows.length+1}`).setNumberFormat('$0.00');
k.tables.add(`A1:F${keywordRows.length+1}`,true,'ExactKeywordScope');k.freezePanes.freezeRows(1);k.freezePanes.freezeColumns(3);
k.getRange('A1:F1').format={fill:'#234766',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},horizontalAlignment:'center',verticalAlignment:'center',rowHeight:30};
wb.recalculate();
const inspection=await wb.inspect({kind:'region',sheetId:'执行结果',range:'A4:E7',maxChars:2500,tableMaxRows:4,tableMaxCols:5});
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:50},maxChars:1500});
await fs.writeFile(path.join(base,'approved-report-inspection.ndjson'),inspection.ndjson);
await fs.writeFile(path.join(base,'approved-report-formula-errors.ndjson'),errors.ndjson);
for(const[sh,range,file]of [['执行结果','A1:F22','approved-report-main.png'],['执行结果',`A${holdTitle}:H${holdLast}`,'approved-report-holds.png'],['执行结果','G10:I20','approved-report-sku.png'],['精准关键词','A1:F16','approved-report-keywords.png']]){
 const img=await wb.render({sheetName:sh,range,scale:1.2,format:'png'});await fs.writeFile(path.join(base,file),new Uint8Array(await img.arrayBuffer()));
}
const out='E:/OpenAI-Codex/天皇のcodex/outputs/01a18a7c-7953-7b83-b51d-1a7f216ae7e1/20261103-approved-ad-execution';
await fs.mkdir(out,{recursive:true});
const filename=path.join(out,'4A广告确认范围与执行结果_20261103.xlsx');
await(await SpreadsheetFile.exportXlsx(wb)).save(filename);
await fs.writeFile(path.join(base,'approved-report-summary.json'),JSON.stringify({filename,newCampaigns:added.length,morningCampaigns:morning.length,oldCampaigns:old.length,totalCampaigns:active.length,newDaily:added.reduce((n,r)=>n+r.daily,0),totalDaily:active.reduce((n,r)=>n+r.daily,0),keywordRows:keywordRows.length,holds:holds.length},null,2));
console.log(JSON.stringify({filename,campaigns:active.length,daily:active.reduce((n,r)=>n+r.daily,0),keywords:keywordRows.length}));
