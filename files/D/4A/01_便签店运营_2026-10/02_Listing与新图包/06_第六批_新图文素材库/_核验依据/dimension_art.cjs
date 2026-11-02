const t=(x,y,z,s,w=400,a='middle',c='#14212b')=>`<text x="${x}" y="${y}" font-size="${z}" font-weight="${w}" text-anchor="${a}" fill="${c}">${s}</text>`;
const rect=(x,y,w,h,c)=>`<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${c}" filter="url(#s)"/>`;
const ar=(x1,y1,x2,y2)=>`<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#61727b" stroke-width="3" marker-start="url(#a)" marker-end="url(#a)"/>`;
const base=b=>`<svg xmlns="http://www.w3.org/2000/svg" width="2000" height="2000"><defs><filter id="s" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="7" stdDeviation="9" flood-opacity=".11"/></filter><marker id="a" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto-start-reverse"><path d="M0 0L8 4L0 8Z" fill="#61727b"/></marker></defs><rect width="2000" height="2000" fill="white"/><g font-family="Arial,sans-serif">${b}</g></svg>`;
function holder(){let b=t(1000,150,88,'One holder. Five hundred ideas.',700)+t(1000,245,46,'400 note sheets + 100 page flags included');
b+=rect(240,520,660,660,'#f1f85b')+ar(240,440,900,440)+`<rect x="480" y="395" width="180" height="85" fill="white"/>`+t(570,458,47,'3 in');
b+=ar(150,520,150,1180)+`<rect x="70" y="810" width="160" height="85" fill="white"/>`+t(150,872,45,'3 in');
b+=t(570,1300,71,'400 sheets',700)+t(570,1380,40,'8 colors × 50 sheets');
const colors=['#f1f85b','#f4b3a0','#ffa533','#f64fbb','#f0f0ed','#a9d83d','#4aafd6','#784aa4'];colors.forEach((c,i)=>b+=rect(230+i*85,1450,65,65,c));
b+=rect(1170,650,220,385,'#f651b9')+rect(1510,650,220,385,'#ffca43');
b+=ar(1170,565,1390,565)+`<rect x="1205" y="520" width="150" height="85" fill="white"/>`+t(1280,582,44,'1 in');
b+=ar(1810,650,1810,1035)+`<rect x="1740" y="800" width="140" height="85" fill="white"/>`+t(1810,860,34,'1 3/4 in');
b+=t(1450,1200,69,'100 flags',700)+t(1450,1280,39,'2 pads × 50 flags')+t(1450,1415,35,'Sticky tabs + Sign Here tabs');
b+=`<line x1="200" y1="1630" x2="1800" y2="1630" stroke="#dce2e6" stroke-width="2"/>`+t(1000,1730,53,'3 pen compartments · 2 side flag pockets',600)+t(1000,1830,43,'Keep everyday notes and markers together.')+t(1000,1930,29,'Paper and tab dimensions shown. Pens not included.',400,'middle','#65737c');return base(b);}
function big(){let b=t(1000,150,88,'A bigger canvas for your ideas.',700)+t(1000,245,48,'11 × 11 in · Four soft pastel pads');
b+=rect(300,440,1100,1100,'#f5bfd3')+rect(300,1240,300,300,'#f3ef9a')+ar(300,350,1400,350)+`<rect x="710" y="305" width="280" height="85" fill="white"/>`+t(850,367,47,'11 in');
b+=ar(205,440,205,1540)+`<rect x="110" y="945" width="190" height="85" fill="white"/>`+t(205,1007,45,'11 in');
b+=t(450,1360,39,'3 × 3 in',600)+t(450,1425,27,'reference size')+t(450,1470,27,'not included');
b+=t(1685,735,94,'13.4×',700)+t(1685,815,37,'the paper area')+t(1685,875,32,'of a 3 × 3 in note');
b+=t(1685,1060,70,'4 pads',700)+t(1685,1150,37,'30 sheets each')+t(1685,1280,70,'120',700)+t(1685,1340,37,'sheets total');
b+=t(1000,1700,51,'Pink · Yellow · Blue · Mint green',600)+t(1000,1810,42,'Room for notes, sketches and shared plans.')+t(1000,1920,29,'Area comparison: 121 ÷ 9 = 13.44. Both paper sizes use the same scale.',400,'middle','#65737c');return base(b);}
exports.makeSvg=id=>({HOLDER303_02:holder,BP1111_02:big}[id])();
exports.svgMetrics=id=>id==='HOLDER303_02'?{paper_scale_px_per_in:220,note_px:[660,660],note_in:[3,3],tab_px:[220,385],tab_in:[1,1.75],notes:8*50,flags:2*50,total:500,holder_dimensions_not_asserted:true}:{paper_scale_px_per_in:100,large_px:[1100,1100],reference_px:[300,300],large_in:[11,11],reference_in:[3,3],area_ratio:121/9,pads:4,total_sheets:120};
