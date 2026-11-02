import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const dir=path.dirname(fileURLToPath(import.meta.url));
const data=JSON.parse(await fs.readFile(path.join(dir,'analysis.json'),'utf8'));
const live=JSON.parse(await fs.readFile(path.join(dir,'live_audit.json'),'utf8'));
const out='E:/OpenAI-Codex/天皇のcodex/outputs/01a18a7c-7953-7b83-b51d-1a7f216ae7e1';
await fs.mkdir(out,{recursive:true});
const wb=Workbook.create();
const sheets=[];
function col(n){let s='';for(n++;n;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;}
function add(name,title,note,headers,rows,widths={}){
 const sh=wb.worksheets.add(name);sheets.push(sh);sh.showGridLines=false;
 const last=col(headers.length-1),end=rows.length+5;
 sh.getRange(`A1:${last}${end}`).format.font={name:'Microsoft YaHei',size:10,color:'#243047'};
 sh.getRange(`A1:${last}${end}`).format.verticalAlignment='center';
 sh.getRange(`A1:${last}${end}`).format.columnWidth=18;
 sh.getRange('A1').values=[[title]];sh.getRange('A1').format.font={bold:true,size:15};
 sh.getRange('A1').format.rowHeight=28;
 sh.getRange('A3').values=[[note]];sh.getRange('A3').format.font={size:10,color:'#64748B'};
 sh.getRange(`A5:${last}5`).values=[headers];
 sh.getRange(`A5:${last}5`).format={fill:'#243B5A',font:{color:'#FFFFFF',bold:true},wrapText:true,rowHeight:36,horizontalAlignment:'center'};
 if(rows.length){sh.getRange(`A6:${last}${end}`).values=rows;sh.getRange(`A6:${last}${end}`).format.wrapText=true;sh.getRange(`A6:${last}${end}`).format.rowHeight=64;sh.tables.add(`A5:${last}${end}`,true,`Data${sheets.length}`);}
 for(const [c,w] of Object.entries(widths))sh.getRange(`${c}:${c}`).format.columnWidth=w;
 sh.freezePanes.freezeRows(5);sh.freezePanes.freezeColumns(2);
 return sh;
}
const overview=wb.worksheets.add('经营总览');sheets.push(overview);overview.showGridLines=false;
overview.getRange('A1:C45').format.font={name:'Microsoft YaHei',size:11,color:'#243047'};
overview.getRange('A:A').format.columnWidth=36;overview.getRange('B:B').format.columnWidth=16;overview.getRange('C:C').format.columnWidth=77;
overview.getRange('A1').values=[['4A 库存、分类与合并复核']];overview.getRange('A1').format.font={size:16,bold:true};overview.getRange('A1').format.rowHeight=30;
overview.getRange('A3').values=[['商品清单：2026-10-31；物流库存快照：2026-10-30；前台抽查：2026-10-31']];
overview.getRange('A5:C5').values=[['核对项目','结果','口径与处理状态']];
const stats=data.stats;
const metrics=[
 ['当前商品SKU',stats.rows,'全量793条，不把Inactive、Incomplete自动当作无价值'],
 ['不同ASIN',stats.asins,'包含父SKU及占位记录'],
 ['有可售库存FNSKU',stats.fba_positive_fnskus,'原报告133个SKU行；同一FNSKU重复行不重复计数'],
 ['FBA可售件数',stats.fba_available_dedup,'已知数量按FNSKU去重；另有2个FNSKU数量为空'],
 ['FBA预留件数',stats.fba_reserved_dedup,'不与可售数量混为同一指标'],
 ['FBA在途件数',stats.fba_inbound_dedup,'尚非可售现货'],
 ['近30天有出货FNSKU',stats.fba_positive_sales30,'不把销量栏空白当作0'],
 ['FBA近30天发货额（USD）',stats.fba_sales30_dedup,'仅此物流报告的发货口径，不代表全店订单销售额'],
 ['FBA近30天日均（USD）',null,'按30天平均，无法替代全店业务报告'],
 ['删名单中仍有可售SKU',stats.deleted_with_available,'17个SKU合计423件；跨日证据，未认定已损失'],
 ['上述可售件数',stats.deleted_available_units,'另1个删名单SKU有1件预留、近30天出货23件'],
 ['内部功能品类',stats.types,'12大类、56功能品类；进一步按规格分141组'],
 ['尚缺产品信息SKU',stats.unknown_skus,'保留待核，未强行塞入默认303家族'],
 ['后台写入次数',0,'本轮未恢复、未删除、未重新合并、未改价'],
 ['前台成功读取页面',live.length,'已确认PSS及其他家族存在；旧评分不得当现值'],
 ['文本匹配待复核配对',data.merge.length,'部分已聚合，需结合前台结果，不是13组新建指令'],
 ['有货且30天动销FBA SKU',40,'当前Active＋FBA＋可售>0＋30天出货>0，接近截图约41款的核心口径']
];
overview.getRange(`A6:C${metrics.length+5}`).values=metrics;overview.getRange(`A6:C${metrics.length+5}`).format.wrapText=true;overview.getRange(`A6:C${metrics.length+5}`).format.rowHeight=38;
overview.getRange('B14').formulas=[['=B13/30']];overview.getRange('B13:B14').setNumberFormat('"$"#,##0.00');
overview.getRange('A24:C24').values=[['当前SKU经营层','SKU数','说明']];
const ops=Object.entries(stats.operations).map(([a,b])=>[a,b,a.includes('零库存')?'仍需结合补货计划、页面价值与当前后台原因判断':'以清单和物流报告精确SKU/ASIN关联']);
overview.getRange(`A25:C${24+ops.length}`).values=ops;overview.getRange(`A25:C${24+ops.length}`).format.wrapText=true;overview.getRange(`A25:C${24+ops.length}`).format.rowHeight=42;
for(const r of ['A5:C5','A24:C24'])overview.getRange(r).format={fill:'#243B5A',font:{color:'#FFFFFF',bold:true},rowHeight:30};
overview.getRange('A39').values=[['处理原则：保留已生效的正确聚合，先修库存关联和错误规格；历史评价不相加。']];
overview.getRange('A41').values=[['现阶段正式交付为核对表；后台连接未附着，恢复与属性修正尚未执行。']];

add('前台实查','已生效结构与局部问题','来源：各行Amazon页面；当前展示不证明销量增长由此次修改造成。',
 ['型号','抽查ASIN','当前父ASIN','当前星级','当前评价数','判断','具体问题','处理方向','来源URL'],
 live.map(x=>[x.name,x.asin,x.parent,x.rating,x.reviews,x.result,x.issue,x.action,x.url]),{A:24,B:18,C:21,D:12,E:14,F:45,G:65,H:60,I:55});
const liveMap=new Map();for(const x of live)for(const a of x.members)liveMap.set(a,x);
function ratingFor(asin,historical){const x=liveMap.get(asin);return x?.asin===asin?`${x.rating}分/${x.reviews}评（本页实查）`:historical?historical+'（历史，未刷新）':x?'同族；本子体评分未单查':'未取得';}
const merge=data.merge.map(r=>{const a=liveMap.get(r[0]),b=liveMap.get(r[3]);let status='两侧当前结构仍待核实';if(a&&b)status=a.parent===b.parent?'已在同族，优先局部修正':'前台仍在不同家族，不能仅按历史评价决定迁移';else if(a)status='已读取有货侧，另一侧关系待核';return [r[0],r[1],ratingFor(r[0],r[2]),r[3],r[4],ratingFor(r[3],r[5]),status,r[7],r[8],r[9],r[10],r[12],r[13],r[15],'未提交后台'];});
add('同款配对','同款页面与库存配对','颜色与实物仍需核对；已同族的配对不重复新建，评分为空不等于无评价。',
 ['有货侧ASIN','快照可售','页面评分参考','另一ASIN','快照可售','页面评分参考2','当前核对状态','功能','尺寸','装量','颜色文本分组','有货侧SKU','另一侧SKU','下一步','执行状态'],merge,{A:18,B:14,C:27,D:18,E:14,F:27,G:55,H:24,I:22,J:16,K:24,L:52,M:52,N:65,O:20});
add('库存补救','有库存或预留在途但报价异常','来源：10-30物流快照与10-31商品报告。原SKU恢复必须先读当前滞留原因。',
 ['SKU','ASIN','FNSKU','可售','预留','在途','不可售','30天出货','30天发货额USD','在100删除名单','当前清单状态','同FNSKU在售SKU','同ASIN在售FBA SKU','处理方向','执行状态'],data.urgent,{A:32,B:18,C:18,D:11,E:11,F:11,G:11,H:14,I:18,J:18,K:20,L:45,M:45,N:65,O:28});
add('分类总览','功能与规格细分','分类为内部管理分组，不能等同于允许创建的Amazon变体父体。',
 ['大类','细分组','SKU数','ASIN数','Active数','FBA SKU数','Incomplete数','说明'],data.summary,{A:21,B:62,C:13,D:13,E:14,F:16,G:18,H:38});
const fields=['sku','asin','status','channel','op','category','fine','dimensions','colors','pads','packsource','packtext','price','quantity','fnsku','available','reserved','inbound','unfulfillable','sold30','sold90','sales30','title','basis','source','asin_skus','parent','old_parent','old_size','old_rating','local_status','live_status'];
const headers=['SKU','ASIN','清单状态','配送渠道','经营层','大类','功能规格细分','尺寸','颜色原文片段','提取本数','本数依据','装量原文','当前价格USD','清单数量（FBA空）','FNSKU','FBA可售','FBA预留','FBA在途','不可售','30天出货','90天出货','30天发货额USD','当前标题','分类参考标题','参考来源','同ASIN SKU数','父命名候选','旧V2父SKU（非现状）','旧V2尺寸（非现状）','历史评分参考','本地处理状态','后台处理状态'];
const master=add('商品主档','793条SKU分类与经营层','商品来源：所有商品报告_10-31-2026.txt。库存为10-30快照；价格仅保留，不作修改。',headers,data.master.map(x=>fields.map(k=>x[k]??null)),{A:34,B:18,C:14,D:19,E:38,F:22,G:62,H:24,I:45,J:12,K:43,L:65,M:18,N:23,O:18,P:14,Q:14,R:14,S:14,T:15,U:15,V:20,W:85,X:85,Y:40,Z:18,AA:18,AB:65,AC:55,AD:24,AE:28,AF:24});
master.getRange(`M6:M${data.master.length+5}`).setNumberFormat('"$"#,##0.00');master.getRange(`V6:V${data.master.length+5}`).setNumberFormat('"$"#,##0.00');
add('物流明细','375条物流记录与清单关联','来源：284701020757.txt，snapshot-date=2026-10-30。重复FNSKU在汇总页去重。',
 ['SKU','ASIN','FNSKU','清单状态','可售','预留','在途','不可售','7天出货','30天出货','90天出货','30天发货额USD','大类','功能','尺寸','物流报告标题','快照日期','同FNSKU在售SKU','同ASIN在售FBA SKU','在删除名单'],data.inventory,{A:34,B:18,C:18,D:25,E:12,F:12,G:12,H:12,I:14,J:15,K:15,L:20,M:22,N:28,O:23,P:85,Q:18,R:50,S:50,T:18});
const unique=data.fba_unique.map(x=>[x.fnsku,x.asin,x.skus.join('；'),x.available,x['Total Reserved Quantity'],x['inbound-quantity'],x['units-shipped-t30'],x['units-shipped-t90'],x['sales-shipped-last-30-days'],x['sales-shipped-last-7-days']]);
add('FNSKU汇总','按FNSKU去重的库存与发货','同市场同FNSKU的重复库存值一致时仅计一次；空白保留，冲突不强行相加。',
 ['FNSKU','ASIN','对应SKU','可售','预留','在途','30天出货','90天出货','30天发货额USD','7天发货额USD'],unique,{A:18,B:18,C:65,D:13,E:13,F:13,G:17,H:17,I:23,J:23});
add('幽灵名单复核','旧隔离名单与删除名单逐条复核','历史数量、历史评分不能冒充当前值；最终判断优先用物流报告和后台滞留原因。',
 ['SKU','ASIN','当前是否存在','清单状态','配送渠道','清单数量','旧隔离表分组','在100删除名单','旧映射库存','旧映射评分','9月原始数量','9月配送渠道','10月FNSKU','10月可售','10月预留','10月在途','30天出货','90天出货','证据状态'],data.ghost,{A:34,B:18,C:52,D:15,E:20,F:15,G:48,H:20,I:18,J:18,K:18,L:20,M:18,N:15,O:15,P:15,Q:15,R:15,S:50});
add('属性问题','需要核对的属性与身份冲突','598条Pack后缀来自旧V2文件；仅前台实查页中明确列出的错误已确认在线显示。',
 ['SKU','ASIN','问题类型','证据与说明','执行状态'],data.issues,{A:36,B:19,C:38,D:110,E:25});
add('原始商品报告','原始商品报告保留','来源：所有商品报告_10-31-2026.txt。保持原文本字段，空白不补0。',Object.keys(data.raw[0]),data.raw.map(x=>Object.values(x)),{A:100,B:70,C:22,D:35,E:15,F:15});
const en=unique.length+5;
overview.getRange('B8').formulas=[[`=COUNTIF('FNSKU汇总'!D6:D${en},">0")`]];
overview.getRange('B9').formulas=[[`=SUM('FNSKU汇总'!D6:D${en})`]];
overview.getRange('B10').formulas=[[`=SUM('FNSKU汇总'!E6:E${en})`]];
overview.getRange('B11').formulas=[[`=SUM('FNSKU汇总'!F6:F${en})`]];
overview.getRange('B12').formulas=[[`=COUNTIF('FNSKU汇总'!G6:G${en},">0")`]];
overview.getRange('B13').formulas=[[`=SUM('FNSKU汇总'!I6:I${en})`]];
overview.getRange('B22').formulas=[[`=COUNTIFS('商品主档'!C6:C798,"Active",'商品主档'!D6:D798,"AMAZON_NA",'商品主档'!P6:P798,">0",'商品主档'!T6:T798,">0")`]];
wb.recalculate();
console.log((await wb.inspect({kind:'table',range:'经营总览!A5:C21',include:'values,formulas',tableMaxRows:17,tableMaxCols:3})).ndjson);
const output=await SpreadsheetFile.exportXlsx(wb);
await output.save(`${out}/4A_库存分类与合并复核_20261031.xlsx`);
for(const sh of sheets){if(process.env.FOURA_QA_SHEETS&&!process.env.FOURA_QA_SHEETS.split(',').includes(sh.name))continue;const range=sh.name==='经营总览'?'A1:C21':sh.name==='前台实查'?'A5:H9':sh.name==='库存补救'?'A5:K10':'A5:F9';try{const p=await wb.render({sheetName:sh.name,range,scale:1,format:'png'});await fs.writeFile(path.join(dir,`preview_${sh.name}.png`),new Uint8Array(await p.arrayBuffer()));console.log('RENDER',sh.name);}catch(e){console.log('RENDER_ERROR',sh.name,e.message);}}
console.log('SAVED',`${out}/4A_库存分类与合并复核_20261031.xlsx`);
