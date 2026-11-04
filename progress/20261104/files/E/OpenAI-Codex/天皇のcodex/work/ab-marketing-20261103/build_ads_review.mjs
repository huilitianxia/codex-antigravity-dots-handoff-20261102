import fs from 'node:fs/promises';
import path from 'node:path';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';

const root = 'E:/OpenAI-Codex/天皇のcodex/work/ab-marketing-20261103';
const out = 'E:/OpenAI-Codex/天皇のcodex/outputs/ab-marketing-20261103';
const pages = JSON.parse(await fs.readFile(path.join(root, 'ads-102-asins-aggregated.json'), 'utf8'));
const scope = JSON.parse(await fs.readFile(path.join(root, 'dots-ads-input/AB_102_ASIN_ADS_SCOPE.json'), 'utf8'));
const raw = JSON.parse(await fs.readFile(path.join(root, 'ads827-matrix.json'), 'utf8'));
const wb = Workbook.create();
const prioritySheet = wb.worksheets.add('重点经营页');
const allSheet = wb.worksheets.add('全部102页面');
const rawSheet = wb.worksheets.add('原始827行广告');
const associationSheet = wb.worksheets.add('已核活动关联');
const period = '2026-10-26 至 2026-11-02';
const priorityByAsin = new Map(scope.priority_existing_operating_pages.map(p => [p.asin, p]));
const proposals = {
  B1: { action: '先核现有SP消耗与搜索词，优化后再评估加预算', cap: 0, why: '8天花费13.45/归因销售29.97；混合SP/SD口径' },
  B2: { action: '先查原SP商品组；必要时做7天低价点击测试', cap: 3, why: 'FBA可售330、近30天67件；MFN库存4947，不能混算' },
  B3: { action: '核现有5美元/日共享自动活动中的MFN SKU', cap: 0, why: '现有活动关联不等MFN商品实际可投' },
  B4: { action: '核两条旧SP；停投且合格时恢复或单独测试', cap: 3, why: 'MFN1054；本期零花费；保留经营页，不迁移' },
  B5: { action: '核旧活动商品状态，再安排7天低预算测试', cap: 2, why: 'MFN470；FBA近30天1件；历史活动无本期消耗' },
  B6: { action: '仅核有货MFN投放，缺货FBA不新增花费', cap: 2, why: 'MFN435；当前FBA缺货，旧活动关联需分SKU' },
  B17: { action: '核现有5美元/日共享活动中的新MFN SKU', cap: 0, why: '新MFN10件已在售；不能重复创建或再扣来源库存' },
  A6: { action: '条件预览，认证声明核实前暂缓新增广告', cap: 0, why: '旧森林认证声明未证，不是包装冲突' },
};

function proposal(page) {
  const p = priorityByAsin.get(page.asin);
  if (p) return proposals[p.group] || {
    action: '先核可售SKU和原活动；小库存优先复用现有活动', cap: 0,
    why: '尚无足够成交与成本证据支持新增预算',
  };
  const hard = page.holds.filter(x => !x.includes('保留来源页'));
  if (hard.length) return { action: '暂缓受限报价，先解决具体身份/可售限制', cap: null, why: hard.join('；') };
  if (page.performance_class.includes('高于归因销售')) return { action: '先查高消耗活动及目标，不直接增加预算', cap: null, why: page.performance_class };
  if (page.performance_class.includes('成本偏高')) return { action: '优先核成本与投放目标，评估降低无效消耗', cap: null, why: page.performance_class };
  return { action: '保留在全量候选，选定真实经营页和资格后再分配预算', cap: null, why: page.performance_class };
}

function col(n) { let r=''; for (;n;n=Math.floor((n-1)/26)) r=String.fromCharCode(65+(n-1)%26)+r; return r; }
let tableNumber = 0;
function setup(sh, title, subtitle, headers, values, widths) {
  sh.showGridLines = false;
  sh.getRange('B2').values = [[title]];
  sh.getRange('B2').format.font = { name: 'Arial', size: 14, bold: true, color: '#20334D' };
  sh.getRange('B3').values = [[subtitle]];
  sh.getRange('B3').format.font = { name: 'Arial', size: 10, italic: true, color: '#56616F' };
  const end = col(headers.length + 1);
  sh.getRange(`B5:${end}5`).values = [headers];
  if(values.length) sh.getRange(`B6:${end}${values.length+5}`).values = values;
  const whole = sh.getRange(`B5:${end}${values.length+5}`);
  whole.format.font = { name: 'Arial', size: 10, color: '#253242' };
  whole.format.verticalAlignment = 'center';
  whole.format.rowHeight = 33;
  sh.getRange(`B5:${end}5`).format = { fill: '#263C58', font: { name:'Arial', size:10, bold:true, color:'#FFFFFF' }, rowHeight:36, horizontalAlignment:'center', verticalAlignment:'center', wrapText:true };
  sh.getRange('A:A').format.columnWidth = 2;
  widths.forEach((w,i)=>{sh.getRange(`${col(i+2)}:${col(i+2)}`).format.columnWidth=w;});
  sh.freezePanes.freezeRows(5);
  sh.freezePanes.freezeColumns(4);
  sh.tables.add(`B5:${end}${values.length+5}`,true,'AdsReview'+(++tableNumber));
}

const pHeaders=['批次','ASIN','经营SKU','库存口径','本期花费USD','归因销售USD','归因订单','点击','ACOS','结论/下一动作','首轮拟新增上限USD/日','试验天数','当前执行状态'];
const priority = scope.priority_existing_operating_pages.map(p=>pages.find(x=>x.asin===p.asin));
const pValues = priority.map(x=>{
  const p=priorityByAsin.get(x.asin), t=x.ad_totals, q=proposal(x), src=scope.pages.find(y=>y.asin===x.asin);
  let inv='11/2快照MFN最大单报价 '+x.mfn_snapshot_max+'；FBA未提供';
  if(p.group==='B17')inv='已核新MFN10；来源1613；FBA5另列';
  if(p.group==='B2')inv='已核FBA330；MFN4947，两个库存口径';
  if(p.group==='B5')inv='已核MFN470；FBA近30天1件';
  if(p.group==='B6')inv='已核MFN435；FBA缺货';
  const active=src.offers.filter(o=>o.status==='Active');
  const sku=p.group==='B17'?'4A 5059-B00SM-FBM':active.map(o=>o['seller-sku']).join('\n');
  return [p.group,x.asin,sku,inv,t['花费(USD)'],t['销售额(USD)'],t['订单数量'],t['点击量'],null,q.action,q.cap,q.cap?7:null,'尚未新增或修改广告'];
});
setup(prioritySheet,'重点老品广告审查',`${period}；12个已定经营页 + A6条件项；拟预算须先通过SKU/活动核验，未投放`,pHeaders,pValues,[7,15,34,42,14,14,11,9,11,55,18,10,27]);
for(let i=0;i<pValues.length;i++)prioritySheet.getCell(i+5,9).formulas=[[`=IF(G${i+6}>0,F${i+6}/G${i+6},"")`]];
prioritySheet.getRange('F6:G18').setNumberFormat('$0.00');
prioritySheet.getRange('J6:J18').setNumberFormat('0.0%');
prioritySheet.getRange('L6:L18').setNumberFormat('$0.00');
prioritySheet.getRange('D6:E18').format.wrapText=true;
prioritySheet.getRange('K6:K18').format.wrapText=true;
prioritySheet.getRange('B6:N18').format.rowHeight=57;
prioritySheet.getRange('B21').values=[['拟新增预算合计上限/日']];
prioritySheet.getRange('F21').formulas=[['=SUM(L6:L18)']];
prioritySheet.getRange('F21').setNumberFormat('$0.00');
prioritySheet.getRange('B23').values=[['销售额为广告归因，含SP/SD混合；零点击也可能产生展示归因订单，不能直接当利润或SP点击转化。']];
prioritySheet.getRange('B24').values=[['现有预算、商品组状态和利润缺口仍待平台补核；新增支出尚未发生。优惠券由Dragon负责。']];

const aHeaders=['批次','ASIN','角色','重点','已匹配广告SKU数','展示','点击','花费USD','订单','归因销售USD','ACOS','MFN单报价快照最大','库存日期','效果判断','建议动作','拟新增上限USD/日','限制/保留','现券%','广告状态验收'];
const aValues=pages.map(x=>{
 const t=x.ad_totals,q=proposal(x);return[x.labels.join(','),x.asin,scope.pages.find(y=>y.asin===x.asin).roles.join(','),priorityByAsin.has(x.asin)?'优先':'后续候选',x.ad_rows.length,t['展示次数'],t['点击量'],t['花费(USD)'],t['订单数量'],t['销售额(USD)'],null,x.mfn_snapshot_max||null,'2026-11-02 17:30',x.performance_class,q.action,q.cap,x.holds.join('；'),x.coupon.join(','),'尚未完成活动/广告组/商品三层验收'];
});
setup(allSheet,'全部102个页面',`${period}；78页匹配131条广告SKU，24页无匹配不能认定无广告；库存不可跨ASIN相加`,aHeaders,aValues,[10,15,20,13,13,11,9,13,9,15,11,19,21,49,58,18,65,12,49]);
for(let i=0;i<aValues.length;i++)allSheet.getCell(i+5,11).formulas=[[`=IF(K${i+6}>0,I${i+6}/K${i+6},"")`]];
allSheet.getRange('I6:I107').setNumberFormat('$0.00');allSheet.getRange('K6:K107').setNumberFormat('$0.00');allSheet.getRange('L6:L107').setNumberFormat('0.0%');
allSheet.getRange('Q6:Q107').setNumberFormat('$0.00');
allSheet.getRange('O6:P107').format.wrapText=true;allSheet.getRange('R6:R107').format.wrapText=true;allSheet.getRange('B6:T107').format.rowHeight=48;

setup(rawSheet,'官方商品广告原始827行',`${period}；CSV原件完整保留；状态和类型列原本为空`,raw.headers,raw.rows,raw.headers.map((x,i)=>i===0?57:i===1||i===2?12:17));
for (const c of ['F','L','M','R']) rawSheet.getRange(`${c}6:${c}832`).setNumberFormat('$0.00');
for (const c of ['I','J','N','P','T']) rawSheet.getRange(`${c}6:${c}832`).setNumberFormat('#,##0');
for (const c of ['H','K','O','Q','S']) rawSheet.getRange(`${c}6:${c}832`).setNumberFormat('0.00%');
rawSheet.getRange('G6:G832').setNumberFormat('0.00');
const associationData=[];
for(const name of await fs.readdir(root)){
 if(!/^adassoc-B[A-Z0-9]{9}\.json$/.test(name))continue;
 const x=JSON.parse(await fs.readFile(path.join(root,name),'utf8'));
 for(const r of x.advertising||[]){for(const l of r.links||[]){if(l.href.includes('/campaigns/'))associationData.push([x.asin,r.id.split('__')[0].slice(11),l.text,(l.href.match(/\/campaigns\/([^/?]+)/)||[])[1]||'',null,'活动关联已见；启停和商品组待核',x.checked_at,l.href]);}}
}
associationData.push(['B07FKG29KB','4A GM30315','sticky notes 3 x 3 basic','A00518052DBISFQIUFPXH',null,'活动关联已见；启停待核','2026-11-03','']);
associationData.push(['B07FKG29KB','4A GM30315','sticky notes 303','A055059430D51LZT65CF9',null,'活动关联已见；启停待核','2026-11-03','']);
associationData.push(['B00SMEFFRE','4A 304 Full Glue','SP_满胶系列_To B_KW EXACT_20250731','A09489521UKBV78MYF8X1','404336631456863','活动已暂停，组开关启用；含6商品，不整组盲恢复','2026-11-03','https://advertising.amazon.com/campaign-manager/sp/campaigns/A09489521UKBV78MYF8X1/ad-groups?entityId=ENTITY2EFMPU8GWXHSP']);
const distinct=[...new Map(associationData.map(x=>[x.slice(0,4).join('|'),x])).values()];
setup(associationSheet,'已核现有活动关联','此表仅列已完成下钻的部分；关联不是投放成功，未知预算/竞价不填0',['ASIN','SKU','活动名','活动ID','广告组ID','当前核实状态','核实时间','证据入口'],distinct,[15,31,55,30,26,68,28,90]);
associationSheet.getRange(`G6:G${distinct.length+5}`).format.wrapText=true;

wb.recalculate();
await fs.mkdir(out,{recursive:true});
for(const [name,range,filename]of[['重点经营页','B2:K18','priority-preview'],['全部102页面','B2:L15','all102-preview'],['原始827行广告','B2:K15','raw827-preview'],['已核活动关联','B2:G15','associations-preview']]){
 const b=await wb.render({sheetName:name,range,scale:1.35,format:'png'});await fs.writeFile(path.join(out,filename+'.png'),new Uint8Array(await b.arrayBuffer()));
}
const check=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:30},maxChars:2000});
await fs.writeFile(path.join(root,'workbook-formula-check.json'),check.ndjson||JSON.stringify(check));
const artifact=await SpreadsheetFile.exportXlsx(wb);await artifact.save(path.join(out,'A-B老品广告效果与执行审查_20261103.xlsx'));
console.log(JSON.stringify({output:path.join(out,'A-B老品广告效果与执行审查_20261103.xlsx'),priority:pValues.length,pages:aValues.length,raw:raw.rows.length,associations:distinct.length}));
