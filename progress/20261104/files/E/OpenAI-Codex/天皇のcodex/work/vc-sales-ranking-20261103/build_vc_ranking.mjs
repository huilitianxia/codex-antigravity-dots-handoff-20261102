import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';

const base=path.dirname(fileURLToPath(import.meta.url));
const data=JSON.parse(await fs.readFile(path.join(base,'ranking-source.json'),'utf8'));
const outputDir='E:/OpenAI-Codex/天皇のcodex/outputs/01a18a7c-7953-7b83-b51d-1a7f216ae7e1/20261103-vc-sales-ranking';
await fs.mkdir(outputDir,{recursive:true});
const wb=Workbook.create();
const rank=wb.worksheets.add('VC销售额排名');
const raw=wb.worksheets.add('VC原始明细');
rank.showGridLines=false;raw.showGridLines=false;
const rawFirst=5,rawLast=rawFirst+data.rows.length-1,first=9,last=first+data.rows.length-1;
raw.getRange('A1').values=[['来源：Amazon VC销量汇总(周订单+批发单+直接订单).xlsx，工作表“全渠道款式销量汇总”。区间2015—2024年。']];
raw.getRange('A2').values=[['保留原明细值及原排名；略过原表100—102行空白行。AF列记录原工作表行号。ASIN沿用VC历史原表，未替换成SC经营页ASIN。']];
raw.getRange(`A4:AF${rawLast}`).values=[[...data.headers,'原表行号'],...data.rows.map(r=>[...r.values,r.source_row])];
raw.getRange(`A4:AF${rawLast}`).format.font={name:'Arial',size:10};
raw.getRange(`A4:AF${rawLast}`).format.verticalAlignment='center';
raw.getRange(`A5:AF${rawLast}`).format.rowHeight=24;
raw.getRange('A4:AF4').format.wrapText=true;raw.getRange('A4:AF4').format.rowHeight=42;
const rawWidths=[['A',10],['B',38],['C',19],['D',16],['E',19],['F',15],['G',19],['H',20],['I',20],['J',22],['K',20],['L',20],['M',22],['N',16],['O',16],['P',18],['Q',16],['R',16],['S',16],['AD',14],['AE',80],['AF',18]];
for(const [c,width] of rawWidths)raw.getRange(`${c}1:${c}${rawLast}`).format.columnWidth=width;
for(const c of ['T','U','V','W','X','Y','Z','AA','AB','AC'])raw.getRange(`${c}4:${c}${rawLast}`).format.columnWidth=13;
for(const c of ['E','K','L','M'])raw.getRange(`${c}5:${c}${rawLast}`).setNumberFormat('$#,##0.00');
raw.getRange(`G5:G${rawLast}`).setNumberFormat('$0.0000');
raw.getRange(`F5:F${rawLast}`).setNumberFormat('0.000%');
raw.getRange(`AE5:AE${rawLast}`).format.wrapText=true;
raw.tables.add(`A4:AF${rawLast}`,true,'VCHistoricalSource');raw.freezePanes.freezeRows(4);raw.freezePanes.freezeColumns(3);
raw.getRange('AH3:AJ3').values=[['原表核对','明细','渠道概览']];
raw.getRange('AH4:AJ7').values=[['型号数',315,316],['总金额（USD）',1131160.05,1133461.17],['总销量（件）',286393,287617],['缺ASIN条数',26,null]];
raw.getRange('AK3').values=[['明细减概览']];
raw.getRange('AK4:AK6').formulas=[['=AI4-AJ4'],['=AI5-AJ5'],['=AI6-AJ6']];
raw.getRange('AI5:AK5').setNumberFormat('$#,##0.00;-$#,##0.00');
raw.getRange('AH9').values=[['原表原排名缺36号；渠道概览与现存明细不一致，无法定位差额所属型号，未分摊差额。']];
raw.getRange('AH11').values=[['301×12-N：总销量69,848件，年度合计71,072件，相差1,224件。金额排名仍沿用原表总金额。']];
raw.getRange('AH3:AK11').format.font={name:'Arial',size:10};
raw.getRange('AH3:AH11').format.columnWidth=75;
raw.getRange('AI3:AK11').format.columnWidth=21;
raw.getRange('AH9:AH11').format.wrapText=true;
raw.getRange('AH9:AH11').format.rowHeight=45;

rank.getRange('A2').values=[['VC历史销售额排名（2015—2024）']];
rank.getRange('A2').format.font={name:'Arial',size:14,bold:true};
rank.getRange('A4:G4').values=[['明细总金额',null,null,'型号数',null,'ASIN待补',null]];
rank.getRange('B4').formulas=[[`=SUM('VC原始明细'!E${rawFirst}:E${rawLast})`]];
rank.getRange('E4').formulas=[[`=COUNTA('VC原始明细'!B${rawFirst}:B${rawLast})`]];
rank.getRange('G4').formulas=[[`=COUNTBLANK('VC原始明细'!C${rawFirst}:C${rawLast})`]];
rank.getRange('B4').setNumberFormat('$#,##0.00');
rank.getRange('A5').values=[['口径：周订单、批发单、直接订单合计；以原表“总金额（USD）”降序重排，同金额并列。ASIN为VC历史原表ASIN。']];
rank.getRange('A6').values=[['原表概览比明细多1款、1,224件、$2,301.12。本排名仅包含现存315条明细；26条缺ASIN，未作推定补码。']];
rank.getRange('A7').values=[['浅蓝色标记截图中的三款：301×12-N、354818、301×12-Y。它们在当前买家页内可直接切换；广告尚未调整。']];
rank.getRange('A5:A7').format.font={name:'Arial',size:9,color:'#595959'};
rank.getRange('A8:H8').values=[['金额排名','商品型号','VC历史ASIN','总金额（USD）','总销量（件）','金额占比','最近出货','核对备注']];
const sourceIndex=new Map(data.rows.map((r,i)=>[r.source_row,rawFirst+i]));
for(let i=0;i<data.ranking.length;i++) {
  const item=data.ranking[i],v=item.values,r=first+i,s=sourceIndex.get(item.source_row);
  rank.getRange(`A${r}:F${r}`).formulas=[[
    `=1+COUNTIFS($D$${first}:$D$${last},">"&D${r})`,
    `='VC原始明细'!B${s}`,
    `=IF('VC原始明细'!C${s}="","待补（原表空白）",'VC原始明细'!C${s})`,
    `='VC原始明细'!E${s}`,
    `='VC原始明细'!D${s}`,
    `=D${r}/SUM('VC原始明细'!$E$${rawFirst}:$E$${rawLast})`,
  ]];
  const date=v[18]&&/^\d{4}\/\d{2}\/\d{2}$/.test(String(v[18]))?new Date(String(v[18]).replaceAll('/','-')+'T00:00:00Z'):null;
  const notes=[v[30]||'',!v[2]?'原表无ASIN':'',item.annual_delta?`原表年度销量与总销量相差${item.annual_delta.toLocaleString('en-US')}件`:'',String(v[1])==='1.75'?'型号字段异常，待核':''].filter(Boolean).join('；');
  rank.getRange(`G${r}:H${r}`).values=[[date,notes]];
  const visualLength=[...notes].reduce((n,c)=>n+(c.charCodeAt(0)>255?2:1),0);
  rank.getRange(`A${r}:H${r}`).format.rowHeight=Math.max(25,Math.min(100,Math.ceil(visualLength/63)*15+8));
}
rank.getRange(`A8:H${last}`).format.font={name:'Arial',size:10};
rank.getRange(`A8:H${last}`).format.verticalAlignment='center';
rank.getRange(`H${first}:H${last}`).format.wrapText=true;
for(const [c,width]of[['A',12],['B',39],['C',25],['D',22],['E',18],['F',16],['G',17],['H',78]])rank.getRange(`${c}1:${c}${last}`).format.columnWidth=width;
rank.getRange(`D${first}:D${last}`).setNumberFormat('$#,##0.00');rank.getRange(`E${first}:E${last}`).setNumberFormat('#,##0');rank.getRange(`F${first}:F${last}`).setNumberFormat('0.0%');rank.getRange(`G${first}:G${last}`).setNumberFormat('yyyy-mm-dd');
rank.getRange(`A${first}:H${last}`).conditionalFormats.addCustom(`OR($C${first}="B01LVTWP7Q",$C${first}="B07DJKDB63",$C${first}="B01LVWFZVZ")`,{fill:'#E7F0FA'});
rank.getRange(`C${first}:C${last}`).conditionalFormats.addCustom(`$C${first}="待补（原表空白）"`,{fill:'#FFF2CC'});
rank.tables.add(`A8:H${last}`,true,'VCSalesRank');rank.freezePanes.freezeRows(8);rank.freezePanes.freezeColumns(3);
wb.recalculate();
const inspection=await wb.inspect({kind:'region',sheetId:'VC销售额排名',range:'A4:H15',maxChars:3500,tableMaxRows:12,tableMaxCols:8});
await fs.writeFile(path.join(base,'inspection.ndjson'),inspection.ndjson);
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:50},maxChars:1500});
await fs.writeFile(path.join(base,'formula-errors.ndjson'),errors.ndjson);
for(const[name,range,file]of[['VC销售额排名','A2:H20','rank-preview.png'],['VC原始明细','AH3:AK11','source-audit-preview.png']]){
  const image=await wb.render({sheetName:name,range,scale:1.5,format:'png'});
  await fs.writeFile(path.join(base,file),new Uint8Array(await image.arrayBuffer()));
}
const result=await SpreadsheetFile.exportXlsx(wb);
const destination=path.join(outputDir,'VC历史销售额排名_ASIN_2015-2024.xlsx');
await result.save(destination);
console.log(JSON.stringify({destination,rows:data.rows.length,missingASIN:26,detailAmount:1131160.05,overviewDifference:2301.12}));
