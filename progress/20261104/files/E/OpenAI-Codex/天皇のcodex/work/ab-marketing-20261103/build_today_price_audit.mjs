import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const base=path.dirname(fileURLToPath(import.meta.url));
const d=JSON.parse(await fs.readFile(path.join(base,'today-ad-price-threeway-analysis.json'),'utf8'));
const suggestions={
 B07FK7PBHJ:'FBM $19.99，高于同页自家FBA $17.99；候选降至$17.99+运费。FBA SKU标NGGrid，须先复核黄/红卷实物身份。',
 B07RQ7JMV9:'FBM促销$11.70，比FBA $11.04高$0.66。按FOB及B档运费预算，直接对齐会亏约$0.11（广告前）；先核实际运费，不进入上传批次。',
 B07B8RBCKT:'FBM $12.39，比FBA $11.99高$0.40。对齐后按FOB及B档预算仅余约$0.94（广告前）；先核真实成本，再定目标价。',
 B07F2BHFJH:'旧促销$11.39高于FBA常规$10.99，仍覆盖显示；终表同规格2本仅$5.99。先清旧优惠并核算FBA费。',
 B01LVXOCU2:'终表24本$9.49；FBA $14.39、FBM $12.99均明显高。优先复核费用后确定清仓价。',
 B073VPHSJ9:'终表4本$9.49，当前FBA $13.99，高$4.50；核算FBA费后优先调整。',
 B01MXYQPE1:'广告SKU 4A 030为$11.99+4.99，同页另有自家FBM $8.99+4.99；终表也是$8.99。',
 B07R1XLCP4:'当前运费$22.99；终表H档$11.99。复核大件实际运费及模板，不直接全局降运费。',
 B082WMV9NQ:'当前运费$4.99；终表2H档$22.99、整套25磅、4包。复核运单成本，避免运费不足。',
 B01NGWHSK1:'终表未找到黄色18本精确行；前台颜色/Pack 2属性也有冲突。暂不套用混色18本价格。',
 B07FKG29KB:'常规$12.99，促销$11.99，运费$8.99已核实。企业$11.49及3/5/10件优惠已提交，尚待独立回读；买家页暂未显示划线。',
 B01M3N310M:'价格$12.99+4.99；无主推荐报价，High Price原case待回复。非单纯缺广告流量。'
};
const priority=['B07FK7PBHJ','B07RQ7JMV9','B07B8RBCKT','B07F2BHFJH','B01LVXOCU2','B073VPHSJ9','B01MXYQPE1','B07R1XLCP4','B082WMV9NQ','B07FKG29KB'];
const rows=[...d.sku_details].sort((a,b)=>(priority.indexOf(a.asin)<0?999:priority.indexOf(a.asin))-(priority.indexOf(b.asin)<0?999:priority.indexOf(b.asin)));
const wb=Workbook.create(),s=wb.worksheets.add('价格与运费');s.showGridLines=false;s.tabColor='#234766';
s.getRange('A2').values=[['今日广告商品价格与运费核对']];s.getRange('A2').format.font={name:'Arial',size:14,bold:true};
s.getRange('A4').values=[['范围：27款、37个广告SKU；前后台生效价格及运费37/37可对应。所有其他商品仅核查，未批量改价。']];
s.getRange('A5').values=[['优先处理：3款FBM商品价高于同页FBA；5082旧促销覆盖低常规价；301×24及608S高于终表；2款大件运费档位差异。']];
s.getRange('A6').values=[['30315：常规$12.99、促销$11.99、运费$8.99已生效；企业价及阶梯已提交，最终回读仍为旧价，尚未完成。']];
s.getRange('A7').values=[['FBA页面免邮有Prime或满$35等条件；表内FBA运费0只适用于满足页面免邮条件时。未进入结算核验普通账户单件运费。']];
s.getRange('A8').values=[['来源：2026(3)终版Sheet1；Seller Central库存及固定促销；Amazon自家全部报价。11月3日晚快照，地址New York 10001，USD税前。']];
s.getRange('A9').values=[['Excel：24款ASIN直接对应、2款按型号及包装对应、1款黄色18本缺精确行。物流档位为参考，非实际运单成本。']];
s.getRange('A4:A9').format.font={name:'Arial',size:10};
s.getRange('A7:A9').format.font={name:'Arial',size:9,color:'#595959'};
const h=['型号','ASIN','广告SKU','配送','终表折后价','终表FBM运费基准','后台常规价','后台生效价','后台运费','前台商品价','前台运费（条件见说明）','前台含运费','差异与建议','终表行'];
const first=13,last=first+rows.length-1;
const values=rows.map(r=>{let note=suggestions[r.asin]||r.notes||'价格及运费可对应；未发现本轮需立即处理的差异。';if(r.public_coupon!=null)note+=` 另有领券商品价$${r.public_coupon.toFixed(2)}，需满足优惠券条件。`;return[r.name,r.asin,r.sku,r.fulfillment,r.excel_sale,r.excel_shipping,r.backend_regular,r.backend_effective,r.backend_shipping,r.public_price,r.public_shipping,null,note,r.master_row];});
s.getRange(`A12:N${last}`).values=[h,...values];s.getRange(`A12:N${last}`).format.font={name:'Arial',size:10};
s.getRange(`A12:N${last}`).format.verticalAlignment='center';s.getRange(`A${first}:N${last}`).format.rowHeight=64;
for(const c of ['A','B','C','D','M'])s.getRange(`${c}${first}:${c}${last}`).format.wrapText=true;
s.getRange(`E${first}:L${last}`).setNumberFormat('$0.00');s.getRange(`N${first}:N${last}`).setNumberFormat('0');
s.getRange(`L${first}:L${last}`).formulas=rows.map((r,i)=>[`=IF(AND(ISNUMBER(J${first+i}),ISNUMBER(K${first+i})),SUM(J${first+i}:K${first+i}),"n.a.")`]);
const widths=[28,19,45,11,16,20,17,17,15,17,22,18,83,13];
for(let i=0;i<widths.length;i++)s.getRangeByIndexes(0,i,last+3,1).format.columnWidth=widths[i];
s.tables.add(`A12:N${last}`,true,'TodayAdPriceAudit');s.getRange('A12:N12').format={fill:'#234766',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},horizontalAlignment:'center',verticalAlignment:'center',wrapText:true,rowHeight:38};
s.freezePanes.freezeRows(12);s.freezePanes.freezeColumns(3);
s.getRange(`E${first}:E${last}`).conditionalFormats.add('containsBlanks',{format:{fill:'#FFF2CC'}});
wb.recalculate();
const chk=await wb.inspect({kind:'region',sheetId:s.name,range:'E13:L18',maxChars:2200,tableMaxRows:6,tableMaxCols:8});
const err=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:20},maxChars:1200});
await fs.writeFile(path.join(base,'today-price-audit-check.ndjson'),chk.ndjson+'\n'+err.ndjson);
for(const [range,file]of [['A1:H19','today-price-audit-left.png'],['I12:N22','today-price-audit-right.png']]){const img=await wb.render({sheetName:s.name,range,scale:1.15,format:'png'});await fs.writeFile(path.join(base,file),new Uint8Array(await img.arrayBuffer()));}
const out=path.resolve(base,'../../outputs/01a18a7c-7953-7b83-b51d-1a7f216ae7e1/20261103-price-audit');await fs.mkdir(out,{recursive:true});
const filename=path.join(out,'今日广告27款37SKU_后台前台终表价格运费核对_20261103.xlsx');await(await SpreadsheetFile.exportXlsx(wb)).save(filename);
await fs.writeFile(path.join(base,'today-price-audit-output.json'),JSON.stringify({filename,rows:rows.length,asins:27,columns:14,frontend_backend_explained:37},null,2));
console.log(JSON.stringify({filename,rows:rows.length}));
