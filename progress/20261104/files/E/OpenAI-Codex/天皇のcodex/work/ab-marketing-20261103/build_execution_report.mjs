import fs from 'node:fs/promises';
import path from 'node:path';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';

const root = 'E:/OpenAI-Codex/天皇のcodex/work/ab-marketing-20261103';
const out = 'E:/OpenAI-Codex/天皇のcodex/outputs/ab-marketing-20261103';
const final = JSON.parse(await fs.readFile(path.join(root, 'execution-final.json'), 'utf8'));
const ads = JSON.parse(await fs.readFile(path.join(root, 'precision-ad-execution.json'), 'utf8'));
const scope = JSON.parse(await fs.readFile(path.join(root, 'dots-ads-input/AB_102_ASIN_ADS_SCOPE.json'), 'utf8'));
const pages = JSON.parse(await fs.readFile(path.join(root, 'ads-102-asins-aggregated.json'), 'utf8'));
const order = ['B1','B2','B3','B4','B5','B6','B17','A2','A4','A5','A7','A8'];
ads.sort((a,b)=>order.indexOf(a.group)-order.indexOf(b.group));
if (ads.length !== 12 || !ads.every(r=>r.independently_verified)) throw new Error('All 12 campaigns must be independently verified.');
const targets = ads.flatMap(r=>r.verification.dom_targets.rows.map(t=>({group:r.group, asin:r.asin, keyword:t.cells.target.split('\n')[0], bid:Number(t.cells.bid.match(/US\$([0-9.]+)/)[1]), match:t.cells.matchType, status:t.cells.status})));
if (targets.length !== 46 || new Set(scope.pages.map(r=>r.asin)).size !== 102) throw new Error('Scope count mismatch.');

const wb = Workbook.create();
const adSheet = wb.worksheets.add('广告执行');
const promoSheet = wb.worksheets.add('优惠执行');
const targetSheet = wb.worksheets.add('精准关键词');
const allSheet = wb.worksheets.add('全部102页面');
const dark = '#233D58', ink = '#263544', muted = '#687A8B';
function col(n) { let r=''; for(;n;n=Math.floor((n-1)/26))r=String.fromCharCode(65+(n-1)%26)+r; return r; }
let tableNo=0;
function table(sh,title,headers,values,widths,start=8) {
  const last = col(headers.length+1), end=start+values.length;
  sh.showGridLines=false;
  sh.getRange(`B2:${last}${end}`).format.font={name:'Arial',size:10,color:ink};
  sh.getRange(`B2:${last}${end}`).format.verticalAlignment='center';
  sh.getRange('B2').values=[[title]];
  sh.getRange('B2').format.font={name:'Arial',size:14,bold:true,color:dark};
  sh.getRange('B2').format.rowHeight=24;
  sh.getRange(`B${start}:${last}${start}`).values=[headers];
  sh.getRange(`B${start+1}:${last}${end}`).values=values;
  sh.getRange(`B${start}:${last}${start}`).format={fill:dark,font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},horizontalAlignment:'center',verticalAlignment:'center',wrapText:true,rowHeight:34};
  sh.getRange(`B${start+1}:${last}${end}`).format={rowHeight:37,wrapText:true,verticalAlignment:'center'};
  widths.forEach((w,i)=>{sh.getRange(`${col(i+2)}:${col(i+2)}`).format.columnWidth=w;});
  sh.getRange('A:A').format.columnWidth=2;
  sh.freezePanes.freezeRows(start);
  sh.freezePanes.freezeColumns(3);
  sh.tables.add(`B${start}:${last}${end}`,true,'Execution'+(++tableNo));
  return {end,last};
}
function context(sh,cell,text) {
  sh.getRange(cell).values=[[text]];
  sh.getRange(cell).format.font={name:'Arial',size:10,color:muted};
  sh.getRange(cell).format.wrapText=false;
}
const adRows=ads.map(r=>[r.group,r.asin,r.skus.join('\n'),r.daily,r.bid,r.verification.dom_targets.rows.length,'已复核投放',new Date('2026-11-09T12:00:00Z'),r.campaignId]);
table(adSheet,'老品广告执行结果',['批次','ASIN','投放 SKU','日预算 USD','关键词出价 USD','精准词数','当前状态','组合截止日期 PST','活动编号'],adRows,[7,16,36,13,14,11,18,20,31]);
adSheet.tabColor=dark;
adSheet.getRange('B4').values=[['日预算']];adSheet.getRange('C4').formulas=[['=SUM(E9:E20)']];adSheet.getRange('C4').setNumberFormat('"$"0.00');
adSheet.getRange('D4').values=[['组合总额上限 USD']];adSheet.getRange('E4').values=[[final.portfolio.cap]];adSheet.getRange('E4').setNumberFormat('"$"0.00');
adSheet.getRange('F4').values=[['精准关键词']];adSheet.getRange('G4').formulas=[['=SUM(G9:G20)']];
adSheet.getRange('H4').values=[['已复核活动']];adSheet.getRange('I4').formulas=[['=COUNTIFS(H9:H20,"已复核投放")']];
adSheet.getRange('C4:I4').format.font={name:'Arial',size:10,bold:true,color:ink};
adSheet.getRange('E9:F20').setNumberFormat('"$"0.00');
adSheet.getRange('I9:I20').setNumberFormat('yyyy-mm-dd');
adSheet.getRange('G9:G20').setNumberFormat('0');
context(adSheet,'B5','仅统计本轮新增活动。动态竞价仅降低，广告位加价为 0。组合到期或总额用尽后停投。');
context(adSheet,'B6','来源：Amazon Ads，'+final.asof_beijing+'（北京时间）。'+final.portfolio.url);

const promoByAsin=new Map(final.promotion.items.map(r=>[r.asin,r]));
const base=final.base_prices;
const business=final.business_samples;
const promoRows=ads.map(r=>{
  const p=promoByAsin.get(r.asin), held=final.promotion.holds.find(h=>h.asin===r.asin);
  return [r.group,r.asin,p?.sku||held?.sku||r.skus.at(-1),base[r.asin]??null,business[r.asin]??null,p?.price??null,p?.quantity??null,p?.status||'未参与',p?.note||held?.reason||'本轮未新增价格优惠',null];
});
table(promoSheet,'老品优惠执行结果',['批次','ASIN','经营 SKU','促销计算起价 USD','企业价抽查 USD','固定促销价 USD','参与数量','平台状态','说明','按参与量估算让利 USD'],promoRows,[7,16,33,15,15,15,11,18,44,17]);
promoSheet.tabColor='#46637E';
context(promoSheet,'B3',`企业购规则：活跃，后台关联 ${final.business_rule.linkedSkuCount} 个 SKU。单件 2%，2 / 5 / 10 件为 3% / 5% / 7%，不累加。既有手工企业价保留。`);
context(promoSheet,'B4',`${final.promotion.items.length} 款固定价格促销：`+final.promotion.start_pst+' 至 '+final.promotion.end_pst+'（PST）。状态：'+final.promotion.status+'。');
context(promoSheet,'B5','起价取创建页当时计价，不含运费。企业价仅填抽查值。参与量为平台承诺数量，系统延迟时可能超量。');
context(promoSheet,'B6','来源：Seller Central，'+final.asof_beijing+'（北京时间）。'+final.promotion.url);
context(promoSheet,'B7','企业购规则来源：'+final.business_rule.url);
for(let i=0;i<promoRows.length;i++){
  const n=9+i;
  promoSheet.getRange(`K${n}`).formulas=[[`=IF(G${n}="","",(E${n}-G${n})*H${n})`]];
}
promoSheet.getRange('E9:G20').setNumberFormat('"$"0.00');promoSheet.getRange('K9:K20').setNumberFormat('"$"#,##0.00');
promoSheet.getRange('H9:H20').setNumberFormat('#,##0');
promoSheet.getRange('I9:I20').conditionalFormats.add('containsText',{text:'未参与',format:{fill:'#FFF0D5',font:{color:'#9B5B08'}}});
promoSheet.getRange('B22').values=[['按参与量估算让利 USD']];promoSheet.getRange('E22').formulas=[['=SUM(K9:K20)']];promoSheet.getRange('E22').setNumberFormat('"$"#,##0.00');
context(promoSheet,'B24','原百分比版本已在生效前取消。现有两张优惠券的 34 个 ASIN 已逐页核对，与本批候选商品无重叠。');

table(targetSheet,'已复核的精准关键词',['批次','ASIN','关键词','匹配方式','关键词出价 USD','当前状态'],targets.map(r=>[r.group,r.asin,r.keyword,r.match,r.bid,r.status]),[7,16,48,12,17,16],5);
targetSheet.getRange('F6:F51').setNumberFormat('"$"0.00');
context(targetSheet,'B3','来源：Amazon Ads 各广告组的投放页面。'+final.asof_beijing+'（北京时间）。46 行为各广告组的关键词记录。');

const adByAsin=new Map(ads.map(r=>[r.asin,r]));
const sourceByAsin=new Map(pages.map(r=>[r.asin,r]));
const all=scope.pages.map(p=>{
  const a=adByAsin.get(p.asin), promo=promoByAsin.get(p.asin), h=(p.holds||[]).filter(x=>!x.includes('保留来源页'));
  let why=a?'首批重点经营页，已复核具体 SKU 和精准关键词':h.length?h.join('；'):'未纳入首批 12 个重点经营页，维持现有投放';
  if(p.labels.includes('A6')&&!a)why='来源标记森林认证声明待核，本轮未新增广告';
  const previous=sourceByAsin.get(p.asin);
  return [p.labels.join('/'),p.asin,p.name,a?'已新增并复核':'本轮未新增',promo?promo.status:'本轮未新增',why,previous?.ad_rows?.length?'导出已匹配':'导出未匹配，保留未知'];
});
all.sort((a,b)=>(adByAsin.has(b[1])?1:0)-(adByAsin.has(a[1])?1:0));
table(allSheet,'全部 102 个老页面的本轮处置',['来源批次','ASIN','商品','本轮广告','本轮价格折扣','处理依据','历史广告导出匹配'],all,[10,16,58,19,20,48,24],6);
context(allSheet,'B3','102 为来源页面数；企业购关联数按 SKU 计数，两者不作一一对应。');
context(allSheet,'B4','来源：A/B 全量清单及 Dots 11/2 资料，广告导出期 10/26–11/2。未匹配不表示没有广告或没有销量。');
for(let i=0;i<all.length;i++){
  const lines=Math.max(Math.ceil(all[i][2].length/72),Math.ceil(all[i][5].length/28),2);
  allSheet.getRange(`B${i+7}:H${i+7}`).format.rowHeight=Math.max(40,lines*13+9);
}
allSheet.getRange('E7:E108').conditionalFormats.add('containsText',{text:'已新增',format:{font:{bold:true,color:'#1E655B'}}});

wb.recalculate();
const sums={daily:ads.reduce((s,r)=>s+r.daily,0),keywords:targets.length,launched:ads.length,scope:all.length,discounts:final.promotion.items.length};
if(sums.daily!==37||sums.keywords!==46||sums.launched!==12||sums.scope!==102)throw Error('Final totals failed');
for(const p of final.promotion.items){if(!(p.price>0&&p.quantity>0&&p.independently_verified))throw Error('Invalid promotion readback '+p.asin);}
const expectedConcession=final.promotion.items.reduce((s,p)=>s+(base[p.asin]-p.price)*p.quantity,0);
const calculatedConcession=Number(promoSheet.getRange('E22').values[0][0]);
if(Math.abs(calculatedConcession-expectedConcession)>0.005||!Number.isFinite(calculatedConcession))throw Error('Concession calculation does not match verified prices');
sums.potential_concession=calculatedConcession;
await fs.mkdir(out,{recursive:true});
const inspect=await wb.inspect({kind:'table',range:'广告执行!B4:I4',include:'values,formulas',tableMaxRows:2,tableMaxCols:9,maxChars:2500});
await fs.writeFile(path.join(root,'execution-report-summary-inspect.ndjson'),inspect.ndjson);
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:100},summary:'final formula error scan',maxChars:4000});
await fs.writeFile(path.join(root,'execution-report-errors.ndjson'),errors.ndjson);
for(const [sheetName,range,file]of[['广告执行','B2:J21','execution-ads-preview.png'],['优惠执行','B2:K24','execution-promos-preview.png'],['精准关键词','B2:G17','execution-keywords-preview.png'],['全部102页面','B2:H17','execution-102-preview.png']]){
  const preview=await wb.render({sheetName,range,scale:1.5,format:'png'});
  await fs.writeFile(path.join(out,file),new Uint8Array(await preview.arrayBuffer()));
}
const output=await SpreadsheetFile.exportXlsx(wb);
const filename=path.join(out,'A-B老品广告与优惠执行结果_20261103.xlsx');
await output.save(filename);
await fs.writeFile(path.join(root,'execution-report-checks.json'),JSON.stringify({sums,summary:inspect.ndjson,errors:errors.ndjson,filename},null,2));
console.log(JSON.stringify({filename,sums,errors:errors.ndjson}));
