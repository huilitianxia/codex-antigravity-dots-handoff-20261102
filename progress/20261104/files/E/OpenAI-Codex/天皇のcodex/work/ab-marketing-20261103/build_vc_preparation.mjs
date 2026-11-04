import fs from 'node:fs/promises';
import path from 'node:path';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';

const root='E:/OpenAI-Codex/天皇のcodex/work/ab-marketing-20261103';
const out='E:/OpenAI-Codex/天皇のcodex/outputs/01a18a7c-7953-7b83-b51d-1a7f216ae7e1/20261103-vc-ad-preparation';
const data=JSON.parse(await fs.readFile(path.join(root,'full-coverage/vc-execution-preparation.json'),'utf8'));
const wb=Workbook.create();
function worksheet(name){const api=wb.worksheets.add(name);return {api,name,getRange:address=>api.getRange(address),tables:api.tables,freezePanes:api.freezePanes};}
const main=worksheet('投放顺序');
const fba=worksheet('FBA库存利润');
const fbm=worksheet('达拉斯FBM核价');
const kw=worksheet('精准词草案');
const vc=worksheet('VC销量原表');
const color={ink:'#24364B',navy:'#29435D',muted:'#687A8A',amber:'#FFF0CB',red:'#A3302D',green:'#24634A',blue:'#23519B'};
const currency='"$"#,##0.00;("$"#,##0.00);"$"0.00';
const integer='#,##0';
const pct='0.0%;(0.0%);0.0%';
const first=9;
function col(n){let s='';for(;n;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;}
function reference(sh,row,key){return `'${sh.name}'!${sh.columns[key]}${row}`;}
function setup(sh,title,fields,records){
  sh.columns=Object.fromEntries(fields.map((f,i)=>[f.key,col(i+2)]));
  sh.fields=fields;sh.records=records;sh.last=first+records.length-1;
  const end=col(fields.length+1);
  sh.api.showGridLines=false;
  sh.getRange(`B2:${end}${sh.last}`).format={font:{name:'Arial',size:10,color:color.ink},verticalAlignment:'center'};
  sh.getRange('A:A').format.columnWidth=2;
  sh.getRange('B2').values=[[title]];
  sh.getRange('B2').format.font={name:'Arial',size:14,bold:true,color:color.navy};
  sh.getRange('B2').format.rowHeight=25;
  sh.getRange(`B7:${end}7`).format.borders={bottom:{style:'thin',color:'#8CA0B1'}};
  sh.getRange(`B8:${end}8`).values=[fields.map(f=>f.label)];
  sh.getRange(`B8:${end}8`).format={fill:color.navy,font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},horizontalAlignment:'center',verticalAlignment:'center',wrapText:true,rowHeight:42};
  const values=records.map(r=>fields.map(f=>f.value?f.value(r):r[f.key]??null));
  if(values.length)sh.getRange(`B${first}:${end}${sh.last}`).values=values;
  sh.getRange(`B${first}:${end}${sh.last}`).format={rowHeight:34,wrapText:false,verticalAlignment:'center'};
  fields.forEach((f,i)=>{
    const c=col(i+2);
    sh.getRange(`${c}:${c}`).format.columnWidth=f.width??14;
    if(f.fmt){sh.getRange(`${c}${first}:${c}${sh.last}`).setNumberFormat(f.fmt);sh.getRange(`${c}${first}:${c}${sh.last}`).format.horizontalAlignment='right';}
    if(f.wrap)sh.getRange(`${c}${first}:${c}${sh.last}`).format.wrapText=true;
    if(f.input)sh.getRange(`${c}${first}:${c}${sh.last}`).format.font.color=color.blue;
    if(f.missingInput){sh.getRange(`${c}${first}:${c}${sh.last}`).format.fill=color.amber;sh.getRange(`${c}${first}:${c}${sh.last}`).format.font.color=color.blue;}
  });
  sh.freezePanes.freezeRows(8);sh.freezePanes.freezeColumns(3);
  sh.tables.add(`B8:${end}${sh.last}`,true,sh.name==='投放顺序'?'ExecutionQueue':sh.name==='FBA库存利润'?'FbaEconomics':sh.name==='达拉斯FBM核价'?'DallasEconomics':sh.name==='精准词草案'?'KeywordDrafts':'VcHistorical');
  sh.formula=(key,fn)=>{
    const c=sh.columns[key];
    sh.getRange(`${c}${first}:${c}${sh.last}`).formulas=records.map((r,i)=>[fn(first+i,r)]);
    sh.getRange(`${c}${first}:${c}${sh.last}`).format.font.color='#222222';
  };
  return sh;
}
function note(sh,cell,text){sh.getRange(cell).values=[[text]];sh.getRange(cell).format.font={name:'Arial',size:10,color:color.muted};sh.getRange(cell).format.wrapText=false;}
function field(key,label,width=14,fmt){return{key,label,width,fmt};}
function packLabel(r){
  const t=r.title.replace(/,/g,' '),p=[...t.matchAll(/(\d+)\s*Pads?\b/gi)].map(x=>Number(x[1]));
  const s=[...t.matchAll(/(\d[\d,]*)\s*Sheets?\s*Total/gi)].map(x=>Number(x[1].replaceAll(',','')));
  return p.length?`${Math.max(...p)} 本${s.length?' / '+Math.max(...s).toLocaleString('en-US')+' 张':''}`:/roll/i.test(t)?'卷装，套数待回读':'包装数量待回读';
}
const skuRows=[...data.sku_rows].sort((a,b)=>(a.history_rank??999)-(b.history_rank??999)||a.asin.localeCompare(b.asin)||a.sku.localeCompare(b.sku));
const fRows=skuRows.filter(r=>r.fulfillment==='FBA');
const mRows=skuRows.filter(r=>r.fulfillment==='FBM');
const skuIndex=new Map();
fRows.forEach((r,i)=>skuIndex.set(r.sku,{sheet:fba,row:first+i,record:r}));
mRows.forEach((r,i)=>skuIndex.set(r.sku,{sheet:fbm,row:first+i,record:r}));

setup(fba,'FBA 库存与单套利润测算（USD）',[
  field('sku','SKU',29),field('asin','ASIN',16),{...field('pack','当前包装',23),value:packLabel},
  field('fba_available','FBA可售',10,integer),field('fba_buyable','可购买量',11,integer),field('fba_reserved','预留',9,integer),
  field('price','现基础价',12,currency),field('coupon_pct','现券折扣',10,pct),field('scheduled_promo','已排促销价',13,currency),
  field('calc_price','保守计价',12,currency),field('net_receipt','券后商品实收',15,currency),field('referral','销售佣金',12,currency),
  field('fba_fee','FBA配送费',13,currency),field('coupon_fee','券变动手续费',15,currency),
  field('fob_cost','FOB参考成本',15,currency),field('amazon_cost','Amazon Cost参考',18,currency),
  field('ref_profit','现价FOB参考贡献',18,currency),field('ref_margin','现价参考贡献率',17,pct),
  {...field('proposed_price','草案基础价',14,currency),input:true},field('draft_receipt','草案券后实收',15,currency),
  field('draft_profit','草案FOB参考贡献',18,currency),field('draft_margin','草案参考贡献率',17,pct),
  {...field('actual_cogs','实际单套货本',15,currency),missingInput:true},
  {...field('extra_cost','头程仓储等/件',16,currency),missingInput:true},field('net_margin','完整成本后净利率',19,pct),
  field('business_stress','再减7%价参考贡献',19,currency),field('fba_t30_shipped','近30日出货件',15,integer),
  field('coverage_days','覆盖天数',12,'0.0'),{...field('replenish','补货提示',38),wrap:true},
  {...field('cost_match','成本匹配依据',38),wrap:true},field('master_row','主表行',10,integer),field('fee_date','费用快照日',14),
],fRows);
const F=(k,r)=>fba.columns[k]+r;
fba.formula('calc_price',r=>`=IF(ISNUMBER(${F('scheduled_promo',r)}),MIN(${F('price',r)},${F('scheduled_promo',r)}),${F('price',r)})`);
fba.formula('net_receipt',r=>`=${F('calc_price',r)}*(1-${F('coupon_pct',r)})`);
fba.formula('referral',r=>`=MAX(0.3,${F('net_receipt',r)}*$AK$4)`);
fba.formula('coupon_fee',r=>`=IF(${F('coupon_pct',r)}>0,${F('net_receipt',r)}*$AK$5,0)`);
fba.formula('ref_profit',r=>`=IF(AND(ISNUMBER(${F('fob_cost',r)}),ISNUMBER(${F('fba_fee',r)})),${F('net_receipt',r)}-${F('referral',r)}-${F('fba_fee',r)}-${F('coupon_fee',r)}-${F('fob_cost',r)},"待成本")`);
fba.formula('ref_margin',r=>`=IF(ISNUMBER(${F('ref_profit',r)}),${F('ref_profit',r)}/${F('net_receipt',r)},"待成本")`);
fba.formula('draft_receipt',r=>`=IF(ISNUMBER(${F('scheduled_promo',r)}),MIN(${F('proposed_price',r)},${F('scheduled_promo',r)}),${F('proposed_price',r)})*(1-${F('coupon_pct',r)})`);
fba.formula('draft_profit',r=>`=IF(AND(ISNUMBER(${F('fob_cost',r)}),ISNUMBER(${F('fba_fee',r)})),${F('draft_receipt',r)}-MAX(0.3,${F('draft_receipt',r)}*$AK$4)-${F('fba_fee',r)}-IF(${F('coupon_pct',r)}>0,${F('draft_receipt',r)}*$AK$5,0)-${F('fob_cost',r)},"待成本")`);
fba.formula('draft_margin',r=>`=IF(ISNUMBER(${F('draft_profit',r)}),${F('draft_profit',r)}/${F('draft_receipt',r)},"待成本")`);
fba.formula('net_margin',r=>`=IF(AND(ISNUMBER(${F('actual_cogs',r)}),ISNUMBER(${F('extra_cost',r)}),ISNUMBER(${F('fba_fee',r)})),(${F('draft_receipt',r)}-MAX(0.3,${F('draft_receipt',r)}*$AK$4)-${F('fba_fee',r)}-IF(${F('coupon_pct',r)}>0,${F('draft_receipt',r)}*$AK$5,0)-${F('actual_cogs',r)}-${F('extra_cost',r)})/${F('draft_receipt',r)},"待成本")`);
fba.formula('business_stress',r=>`=IF(AND(ISNUMBER(${F('fob_cost',r)}),ISNUMBER(${F('fba_fee',r)})),${F('draft_receipt',r)}*0.93-MAX(0.3,${F('draft_receipt',r)}*0.93*$AK$4)-${F('fba_fee',r)}-IF(${F('coupon_pct',r)}>0,${F('draft_receipt',r)}*0.93*$AK$5,0)-${F('fob_cost',r)},"待成本")`);
fba.formula('coverage_days',r=>`=IF(ISNUMBER(${F('fba_t30_shipped',r)}),IF(${F('fba_t30_shipped',r)}>0,${F('fba_available',r)}/${F('fba_t30_shipped',r)}*30,"近30日无出货"),"缺动销数据")`);
fba.formula('replenish',r=>`=IF(ISNUMBER(${F('coverage_days',r)}),IF(${F('coverage_days',r)}<$AK$7,"低于空运7天，先核达拉斯现货补仓",IF(${F('coverage_days',r)}<$AK$6,"短于海运30天，核达拉斯或空运","可按海运周期排补货")),"按广告测试后的实际动销重算")`);
note(fba,'B3','库存：11月3日08:38导出。配送费：10月31日逐SKU快照。出货基数：10月30日库存规划报告。');
note(fba,'B4','FOB参考贡献已扣现券与变动券费，未扣未提供的完整货本、头程、仓储和退货成本。黄色格补齐后才显示净利率。');
note(fba,'B5','再减7%为企业量价叠加压力测算，不代表每个SKU已生效。既有券固定$5不重复计入新增投放成本。');
note(fba,'B6','来源：官方定价基准终版 Sheet1 J/K/M/O；全量商品报告；285829020760；库存规划284701020757。');
fba.getRange('AJ3:AK7').values=[['参数','值'],['办公用品佣金',0.15],['券变动费率',0.025],['海运周期/天',30],['空运预留/天',7]];
fba.getRange('AK4:AK5').setNumberFormat(pct);fba.getRange('AJ:AJ').format.columnWidth=24;fba.getRange('AK:AK').format.columnWidth=18;
note(fba,'AJ9','费率来源：https://sell.amazon.com/pricing');
note(fba,'AJ10','券费来源：Amazon Danny_Amazon，2025-06-02起$5/券+券销售额2.5%。');
note(fba,'AJ12','海运30天、空运7天由用户本轮提供，指运到美国仓。FBA上架时间另计。');
fba.api.tabColor=color.navy;

setup(fbm,'达拉斯仓 FBM 库存与核价（USD）',[
  field('sku','SKU',30),field('asin','ASIN',16),field('fbm_declared','后台申报库存',15,integer),
  {...field('pack','当前包装',24),value:packLabel},field('price','现基础价',12,currency),
  {...field('shipping_confirmed','买家运费已核',15,currency),missingInput:true},field('shipping_reference','主表运费参考',15,currency),
  field('coupon_pct','现券折扣',10,pct),field('scheduled_promo','已排促销价',13,currency),
  field('net_item','券后商品实收',15,currency),field('delivered','含运费实收已核',17,currency),
  field('referral','销售佣金',12,currency),field('coupon_fee','券变动手续费',15,currency),
  field('fob_cost','FOB参考成本',15,currency),field('amazon_cost','Amazon Cost参考',18,currency),
  {...field('actual_cogs','实际单套货本',15,currency),missingInput:true},
  {...field('inbound_cost','深圳至达拉斯/件',18,currency),missingInput:true},
  {...field('dallas_cost','达拉斯出库包材派送/件',23,currency),missingInput:true},
  field('ref_profit','FOB参考贡献',16,currency),field('ref_margin','参考贡献率',14,pct),
  field('net_profit','完整成本后利润/件',20,currency),field('net_margin','完整成本后净利率',20,pct),
  field('dallas_ceiling','参考运费下达拉斯费用上限',26,currency),
  {...field('proposed_price','草案基础价',14,currency),input:true},
  {...field('draft_shipping','草案买家运费',15,currency),missingInput:true,value:r=>r.shipping_confirmed},
  field('draft_ref_profit','草案FOB参考贡献',18,currency),field('draft_ref_margin','草案参考贡献率',18,pct),
  field('draft_net_margin','草案完整净利率',17,pct),{...field('cost_match','成本匹配依据',38),wrap:true},
  field('master_row','主表行',10,integer),field('shipping_template','当前运费模板',31),
],mRows);
const M=(k,r)=>fbm.columns[k]+r;
const item=(r,price)=>`IF(ISNUMBER(${M('scheduled_promo',r)}),MIN(${price},${M('scheduled_promo',r)}),${price})*(1-${M('coupon_pct',r)})`;
fbm.formula('net_item',r=>`=${item(r,M('price',r))}`);
fbm.formula('delivered',r=>`=IF(ISNUMBER(${M('shipping_confirmed',r)}),${M('net_item',r)}+${M('shipping_confirmed',r)},"待运费")`);
fbm.formula('referral',r=>`=IF(ISNUMBER(${M('delivered',r)}),MAX(0.3,${M('delivered',r)}*0.15),"待运费")`);
fbm.formula('coupon_fee',r=>`=IF(${M('coupon_pct',r)}>0,${M('net_item',r)}*0.025,0)`);
fbm.formula('ref_profit',r=>`=IF(AND(ISNUMBER(${M('delivered',r)}),ISNUMBER(${M('fob_cost',r)}),ISNUMBER(${M('dallas_cost',r)})),${M('delivered',r)}-${M('referral',r)}-${M('coupon_fee',r)}-${M('fob_cost',r)}-${M('dallas_cost',r)},"待达拉斯成本")`);
fbm.formula('ref_margin',r=>`=IF(ISNUMBER(${M('ref_profit',r)}),${M('ref_profit',r)}/${M('delivered',r)},"待成本")`);
fbm.formula('net_profit',r=>`=IF(AND(ISNUMBER(${M('delivered',r)}),ISNUMBER(${M('actual_cogs',r)}),ISNUMBER(${M('inbound_cost',r)}),ISNUMBER(${M('dallas_cost',r)})),${M('delivered',r)}-${M('referral',r)}-${M('coupon_fee',r)}-${M('actual_cogs',r)}-${M('inbound_cost',r)}-${M('dallas_cost',r)},"待完整成本")`);
fbm.formula('net_margin',r=>`=IF(ISNUMBER(${M('net_profit',r)}),${M('net_profit',r)}/${M('delivered',r)},"待成本")`);
fbm.formula('dallas_ceiling',r=>`=IF(AND(ISNUMBER(${M('shipping_reference',r)}),ISNUMBER(${M('fob_cost',r)})),${M('net_item',r)}+${M('shipping_reference',r)}-MAX(0.3,(${M('net_item',r)}+${M('shipping_reference',r)})*0.15)-${M('coupon_fee',r)}-${M('fob_cost',r)},"待参考成本")`);
fbm.formula('draft_ref_profit',r=>`=IF(AND(ISNUMBER(${M('draft_shipping',r)}),ISNUMBER(${M('fob_cost',r)}),ISNUMBER(${M('dallas_cost',r)})),(${item(r,M('proposed_price',r))})+${M('draft_shipping',r)}-MAX(0.3,((${item(r,M('proposed_price',r))})+${M('draft_shipping',r)})*0.15)-IF(${M('coupon_pct',r)}>0,(${item(r,M('proposed_price',r))})*0.025,0)-${M('fob_cost',r)}-${M('dallas_cost',r)},"待成本")`);
fbm.formula('draft_ref_margin',r=>`=IF(ISNUMBER(${M('draft_ref_profit',r)}),${M('draft_ref_profit',r)}/((${item(r,M('proposed_price',r))})+${M('draft_shipping',r)}),"待成本")`);
fbm.formula('draft_net_margin',r=>`=IF(AND(ISNUMBER(${M('draft_shipping',r)}),ISNUMBER(${M('actual_cogs',r)}),ISNUMBER(${M('inbound_cost',r)}),ISNUMBER(${M('dallas_cost',r)})),((${item(r,M('proposed_price',r))})+${M('draft_shipping',r)}-MAX(0.3,((${item(r,M('proposed_price',r))})+${M('draft_shipping',r)})*0.15)-IF(${M('coupon_pct',r)}>0,(${item(r,M('proposed_price',r))})*0.025,0)-${M('actual_cogs',r)}-${M('inbound_cost',r)}-${M('dallas_cost',r)})/((${item(r,M('proposed_price',r))})+${M('draft_shipping',r)}),"待完整成本")`);
note(fbm,'B3','发货地：用户确认美国达拉斯仓。申报库存来自11月3日08:38全量商品报告，未取得达拉斯仓实盘表。');
note(fbm,'B4','海运约30天，急货空运预留7天。黄色格填写实际支出。买家支付的运费收入不能当成仓库实际派送成本。');
note(fbm,'B5','参考运费下费用上限使用原表N/B/H/2H运费，不是当前实收或利润。上限尚须覆盖头程、广告及其他费用。');
note(fbm,'B6','同型号的单包、多包SKU可能共用库存，不累计申报量。成本引用：官方定价基准终版Sheet1，匹配行见表内。');
fbm.api.tabColor='#587085';

const plans=data.plans;
setup(main,'VC 老品广告待执行清单',[
  field('execution_order','顺序',8,integer),field('history_rank','VC原序号',11,integer),
  {...field('model','历史型号 / 当前包装',29),wrap:true,value:p=>{const r=skuIndex.get(p.target_sku).record;return (p.history_sku||r.master_sku||r.sku)+'\n'+packLabel(r);}},
  field('history_units','VC累计件数',14,integer),field('asin','经营ASIN',16),field('target_sku','首选SKU',30),
  {...field('fulfillment','首选履约',11),value:p=>skuIndex.get(p.target_sku).record.fulfillment},
  field('fba_stock','该ASIN FBA可售',16,integer),field('fbm_stock','FBM最大SKU申报',18,integer),
  field('price','现基础价',12,currency),field('draft_price','草案基础价',14,currency),field('margin','草案参考贡献率',18,pct),
  {...field('action','动作草案',22),wrap:true},field('daily_draft','通过后日预算',15,currency),
  field('bid','初始CPC草案',15,currency),field('gate','执行条件',25),
  {...field('detail','上线前核对事项',57),wrap:true,value:p=>{const r=skuIndex.get(p.target_sku).record;const holds=r.holds.filter(x=>x!=='缺实际发货成本');return [...holds,r.promo_warning,'回读现价、现券、企业价、评分及广告资格'].filter(Boolean).join('；');}},
  field('planned_cvr','CPC测算转化率',17,pct),field('cvr_basis','转化率依据',38),
],plans);
const P=(k,r)=>main.columns[k]+r;
main.formula('fba_stock',r=>`=SUMIFS('FBA库存利润'!$${fba.columns.fba_available}$9:$${fba.columns.fba_available}$${fba.last},'FBA库存利润'!$${fba.columns.asin}$9:$${fba.columns.asin}$${fba.last},${P('asin',r)})`);
main.formula('fbm_stock',(r,p)=>{
  const candidates=mRows.map((x,i)=>({x,row:first+i})).filter(x=>x.x.asin===p.asin).sort((a,b)=>b.x.fbm_declared-a.x.fbm_declared);
  return candidates.length?`=${reference(fbm,candidates[0].row,'fbm_declared')}`:'=0';
});
main.formula('price',(r,p)=>{const x=skuIndex.get(p.target_sku);return '='+reference(x.sheet,x.row,'price');});
main.formula('draft_price',(r,p)=>{const x=skuIndex.get(p.target_sku);return '='+reference(x.sheet,x.row,'proposed_price');});
main.formula('margin',(r,p)=>{const x=skuIndex.get(p.target_sku);return '='+reference(x.sheet,x.row,x.record.fulfillment==='FBA'?'draft_margin':'draft_ref_margin');});
main.formula('bid',(r,p)=>{
  if(['维护已有精准','修复已有精准利润'].includes(p.action))return '="复核现有出价"';
  const x=skuIndex.get(p.target_sku),profit=reference(x.sheet,x.row,x.record.fulfillment==='FBA'?'draft_profit':'draft_ref_profit');
  return `=IF(ISNUMBER(${profit}),IF(${profit}>0,ROUND(MIN(0.45,MAX(0.02,${profit}*${P('planned_cvr',r)}*0.7)),2),"待调价"),"待成本")`;
});
main.formula('gate',(r,p)=>{
  const x=skuIndex.get(p.target_sku),nr=reference(x.sheet,x.row,x.record.fulfillment==='FBA'?'net_margin':'draft_net_margin');
  const identity=x.record.holds.some(t=>t!=='缺实际发货成本');
  if(identity)return '="待核规格或成本引用"';
  return `=IF(ISNUMBER(${nr}),IF(${nr}>0,"待后台回读","待调价或降低成本"),"待完整成本")`;
});
note(main,'B3','按VC历史销量排候选页，覆盖不同包装。VC件数按原型号重复引用，不可跨页面相加。全部为草案，尚未上传。');
note(main,'B4','现有22个候选页有有效精准覆盖，其中3页需复核薄利。新增61页待回读、12页需先核调价，其余先补规格或达拉斯成本。');
note(main,'B5','参考贡献率不是净利率。实际成本空白时执行条件保持“待完整成本”。预算按每页7天测试草拟，起止日期在上线当天设。');
note(main,'B6','FBA可售按当前ASIN汇总；FBM展示最大单SKU申报而非实盘或多个SKU之和。原$300限额取消曾提交，仍待回读确认。');
main.api.tabColor=color.navy;
for(const s of [fba,fbm]){
  for(const key of s===fba?['ref_profit','draft_profit','business_stress']:['net_profit','draft_ref_profit']){
    s.getRange(`${s.columns[key]}9:${s.columns[key]}${s.last}`).conditionalFormats.add('cellIs',{operator:'lessThan',formula:0,format:{fill:'#FBE4E2',font:{color:color.red,bold:true}}});
  }
}
main.getRange(`${main.columns.gate}9:${main.columns.gate}${main.last}`).conditionalFormats.add('containsText',{text:'待',format:{font:{color:'#925B18'}}});
main.getRange(`${main.columns.action}9:${main.columns.action}${main.last}`).conditionalFormats.add('containsText',{text:'修复',format:{font:{color:color.red,bold:true}}});

setup(kw,'精准关键词与预算草案',[
  field('order','执行顺序',11,integer),field('model','历史型号',25),field('asin','ASIN',16),field('sku','首选SKU',31),
  field('keyword','关键词',47),field('match','匹配',10),field('bid','CPC草案',15,currency),
  field('daily_draft','所属活动日预算',18,currency),field('action','动作草案',24),field('status','状态',19),
],data.keyword_drafts);
const planMainRow=new Map(plans.map((p,i)=>[p.asin,first+i]));
kw.formula('bid',(r,t)=>'='+reference(main,planMainRow.get(t.asin),'bid'));
note(kw,'B3','每页只建一个精准活动。相同ASIN的其他SKU在核价后追加到该活动，已有效投放的精准活动优先维护。');
note(kw,'B4','日预算按活动重复展示，不可按关键词行相加。仅降低竞价、广告位加价0。规格或成本未通过的词不上传。');
note(kw,'B5','关键词根据当前标题及主表规格起草，批量上传前核对尺寸、颜色、包装数及是否带底座或补充芯。');
note(kw,'B6','来源：本表投放顺序和当前商品报告。广告状态依据11月3日08:41全量广告导出，含零展示与已暂停项目。');

setup(vc,'VC 历史销量原表核对（2015—2024）',[
  field('rank_original','原序号',11,integer),field('sku','历史型号',31),field('asin','VC原ASIN',16),
  field('total_units','原表累计件数',16,integer),field('amount_usd','原表金额USD',18,currency),
  ...Array.from({length:10},(_,i)=>({key:'y'+(2015+i),label:String(2015+i),width:11,fmt:integer,value:r=>r.years[String(2015+i)]??null})),
  field('annual_sum','年度合计',15,integer),field('delta','年度减原表差',17,integer),
  field('last_shipment','最后发货',15),
],data.history);
const V=(k,r)=>vc.columns[k]+r;
vc.formula('annual_sum',r=>`=SUM(${V('y2015',r)}:${V('y2024',r)})`);
vc.formula('delta',r=>`=${V('annual_sum',r)}-${V('total_units',r)}`);
note(vc,'B3','来源：Amazon VC销量汇总（周订单+批发单+直接订单）.xlsx，全渠道款式销量汇总。315条款式，保留原累计列。');
note(vc,'B4','301x12-N原累计69,848，年度合计71,072，差1,224。按原累计列排序，未静默改写或把三渠道重复累计。');
note(vc,'B5','历史销量是排序依据，不等同当前需求。补货覆盖天数使用另有日期的近30日发货记录。');
note(vc,'B6','最后发货日期沿用来源文本，空白保持未知。原表三渠道汇总列保留，不与累计列重复相加。');
vc.getRange(`${vc.columns.delta}9:${vc.columns.delta}${vc.last}`).conditionalFormats.add('cellIs',{operator:'notEqual',formula:0,format:{fill:'#FBE4E2',font:{color:color.red,bold:true}}});
const historicalRows=new Map(data.history.map((h,i)=>[h.rank_original,first+i]));
main.formula('history_units',(r,p)=>p.history_rank==null?'="未匹配"':'='+reference(vc,historicalRows.get(p.history_rank),'total_units'));

await fs.mkdir(out,{recursive:true});
wb.recalculate();
// Independent unit-economics controls on known source rows.
const n=skuIndex.get('4A 301x12-N');
const nProfit=Number(fba.getRange(`${fba.columns.ref_profit}${n.row}`).values[0][0]);
const expectedN=5.99*0.95-5.99*0.95*0.15-3.51-5.99*0.95*0.025-1.75;
if(Math.abs(nProfit-expectedN)>0.000001)throw Error('301x12-N coupon-aware unit economics failed: '+nProfit);
const nNet=fba.getRange(`${fba.columns.net_margin}${n.row}`).values[0][0];
if(nNet!=='待成本')throw Error('Missing actual costs must remain unavailable');
const oldCogs=fba.getRange(`${fba.columns.actual_cogs}${n.row}`).values;
const oldExtra=fba.getRange(`${fba.columns.extra_cost}${n.row}`).values;
fba.getRange(`${fba.columns.actual_cogs}${n.row}`).values=[[1.75]];
fba.getRange(`${fba.columns.extra_cost}${n.row}`).values=[[0]];
wb.recalculate();
if(typeof fba.getRange(`${fba.columns.net_margin}${n.row}`).values[0][0]!=='number')throw Error('A confirmed zero extra cost must calculate');
fba.getRange(`${fba.columns.actual_cogs}${n.row}`).values=oldCogs;
fba.getRange(`${fba.columns.extra_cost}${n.row}`).values=oldExtra;
wb.recalculate();
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:100},maxChars:2500});
await fs.writeFile(path.join(root,'preparation-formula-errors.ndjson'),errors.ndjson);
const inspect=await wb.inspect({kind:'table',range:`FBA库存利润!${fba.columns.price}${n.row}:${fba.columns.net_margin}${n.row}`,include:'values,formulas',tableMaxRows:2,tableMaxCols:22,maxChars:5000});
await fs.writeFile(path.join(root,'preparation-profit-inspect.ndjson'),inspect.ndjson);
const previews=[
  ['投放顺序','B2:M20','queue-preview.png'],
  ['投放顺序','N8:T20','queue-actions-preview.png'],
  ['FBA库存利润','B2:S18','fba-current-preview.png'],
  ['FBA库存利润',`${fba.columns.proposed_price}8:${fba.columns.net_margin}19`,'fba-draft-preview.png'],
  ['达拉斯FBM核价','B2:P18','dallas-preview.png'],
  ['精准词草案','B2:K18','keywords-preview.png'],
  ['VC销量原表','B2:T18','vc-source-preview.png'],
];
for(const [sheetName,range,file] of previews){const blob=await wb.render({sheetName,range,scale:1.5,format:'png'});await fs.writeFile(path.join(out,file),new Uint8Array(await blob.arrayBuffer()));}
const file=path.join(out,'VC老品投放准备_库存利润与精准词_20261103.xlsx');
await (await SpreadsheetFile.exportXlsx(wb)).save(file);
await fs.writeFile(path.join(root,'preparation-workbook-checks.json'),JSON.stringify({file,summary:data.summary,nProfit,expectedN,missingCost:nNet,errors:errors.ndjson,previews:previews.map(x=>x[2])},null,2));
console.log(JSON.stringify({file,summary:data.summary,nProfit,errors:errors.ndjson}));
