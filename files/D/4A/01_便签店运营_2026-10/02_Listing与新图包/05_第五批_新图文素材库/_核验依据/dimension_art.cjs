const ink='#14212b',muted='#65737c';
const t=(x,y,size,text,weight=400,anchor='middle',fill=ink)=>`<text x="${x}" y="${y}" font-size="${size}" font-weight="${weight}" text-anchor="${anchor}" fill="${fill}">${text}</text>`;
const rect=(x,y,w,h,fill,extra='')=>`<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${fill}" ${extra}/>`;
const ar=(x1,y1,x2,y2)=>`<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#61727b" stroke-width="3" marker-start="url(#a)" marker-end="url(#a)"/>`;
const wrap=b=>`<svg xmlns="http://www.w3.org/2000/svg" width="2000" height="2000"><defs><filter id="s" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="8" stdDeviation="10" flood-opacity=".12"/></filter><marker id="a" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto-start-reverse"><path d="M0 0L8 4L0 8Z" fill="#61727b"/></marker><pattern id="glue" width="20" height="20" patternUnits="userSpaceOnUse"><rect width="20" height="20" fill="#c7ddd4"/><path d="M-5 5L5-5M0 20L20 0M15 25L25 15" stroke="#b7d1c5" stroke-width="2"/></pattern></defs><rect width="2000" height="2000" fill="white"/><g font-family="Arial,sans-serif">${b}</g></svg>`;
function adhesive(){let b=t(1000,170,92,'Adhesive across the back.',700)+t(1000,265,48,'Full-adhesive notes with a non-stick lifting edge');
b+=t(510,480,49,'Typical top-strip note',600)+t(1490,480,49,'4A full-adhesive note',600);
b+=rect(220,590,580,580,'#f7f5e9','filter="url(#s)"')+rect(220,590,580,100,'url(#glue)');
b+=rect(1200,590,580,580,'#f7f5e9','filter="url(#s)"')+rect(1200,590,580,530,'url(#glue)');
b+=t(510,1300,40,'Adhesive along the top')+t(1490,1300,40,'Broad adhesive coverage');
b+=`<path d="M1750 1145H1850V1435H1730" fill="none" stroke="#61727b" stroke-width="3"/>`+t(1490,1450,37,'Non-stick lifting edge',500);
b+=rect(480,1600,50,50,'url(#glue)')+t(555,1640,40,'Shaded area = adhesive',400,'start');
b+=rect(1180,1600,50,50,'#f7f5e9','stroke="#d6d9d8" stroke-width="2"')+t(1255,1640,40,'Uncoated edge',400,'start');
b+=t(1000,1790,49,'More coverage for everyday reminders.',600)+t(1000,1900,29,'Coverage illustration only. Adhesive-zone sizes are schematic.',400,'middle',muted);
return wrap(b);}
function fullSize(){let b=t(1000,160,88,'Five colors. Four hundred notes.',700)+t(1000,255,48,'3 × 3 in · 80 sheets per color');
b+=rect(270,590,650,650,'#f2f65a','filter="url(#s)"')+ar(270,500,920,500)+rect(505,452,180,90,'white')+t(595,519,49,'3 in');
b+=ar(165,590,165,1240)+rect(75,870,180,90,'white')+t(165,936,49,'3 in');
b+=t(595,1370,44,'Square full-adhesive notes',600);
const colors=[['Lime','#b9df54'],['Peach','#f4b49b'],['Orange','#ffb136'],['Pink','#f457bc'],['Yellow','#f1f85b']];
colors.forEach((c,i)=>{let y=425+i*205;b+=rect(1120,y,150,150,c[1],'filter="url(#s)"')+t(1320,y+65,45,c[0],600,'start')+t(1320,y+125,37,'80 sheets',400,'start');});
b+=`<line x1="220" y1="1550" x2="1780" y2="1550" stroke="#dce2e6" stroke-width="2"/>`+t(1000,1690,105,'400 sheets',700)+t(1000,1790,45,'5 colors × 80 sheets')+t(1000,1910,29,'Size follows the product packaging. Color swatches are illustrative.',400,'middle',muted);return wrap(b);}
function pssSize(){let b=t(1000,155,92,'Three colors. One dispenser.',700)+t(1000,255,48,'Narrow paper strips for custom-length notes');
b+=t(540,570,70,'0.6 in',700)+t(540,645,42,'wide per strip');
b+=rect(235,800,610,122,'#f4f45b','filter="url(#s)"')+ar(925,800,925,922)+rect(860,832,130,58,'white')+t(925,875,31,'0.6 in');
b+=t(540,1090,80,'315 in',700)+t(540,1170,42,'long per color')+t(540,1350,41,'1 compact dispenser',600)+t(540,1430,38,'Yellow · Orange · Rose pink');
const x0=1160,y0=420,scale=220;
[[2,'#f456b9'],[3,'#ffb03d'],[5,'#f3f75b']].forEach((p,i)=>{let x=x0+i*225;b+=rect(x,y0,.6*scale,p[0]*scale,p[1],'filter="url(#s)"')+t(x+.3*scale,y0+p[0]*scale+65,39,p[0]+' in cut',500);});
b+=t(1450,1705,36,'Example cut lengths',500);
b+=`<line x1="220" y1="1785" x2="1780" y2="1785" stroke="#dce2e6" stroke-width="2"/>`+t(1000,1865,43,'Choose the length you need.',600)+t(1000,1945,28,'Continuous paper strips. Examples shown are not pre-cut pieces.',400,'middle',muted);return wrap(b);}
exports.makeSvg=id=>({FULL303_02:adhesive,FULL303_03:fullSize,PSS93_03:pssSize}[id])();
exports.svgMetrics=id=>id==='FULL303_02'?{comparison_type:'schematic adhesive coverage',paper_square_px:[580,580],exact_glue_zone:false}:id==='FULL303_03'?{square_px:[650,650],square_inches:[3,3],colors:5,sheets_per_color:80,total_sheets:400}:{cut_example_scale_px_per_in:220,width_px:132,width_in:.6,example_cut_lengths_in:[2,3,5],length_per_color_in:315,dispensers:1,colors:3};

