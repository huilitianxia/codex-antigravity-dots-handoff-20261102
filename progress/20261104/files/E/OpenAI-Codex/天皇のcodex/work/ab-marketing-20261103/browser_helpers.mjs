import fs from 'node:fs/promises';
export function connectTools(){
  const b={fs,ops:{},seq:0};
  b.text=r=>r.result?.content?.filter(x=>x.type==='text').map(x=>x.text).join('\n')||JSON.stringify(r);
  b.decode=r=>{if(r.result?.isError)throw Error(b.text(r));const m=b.text(r).match(/```json\n([\s\S]*?)\n```/);if(!m)throw Error(b.text(r));return JSON.parse(m[1]);};
  b.tool=async(name,args={})=>{
    const {id}=await(await fetch('http://127.0.0.1:8768/call',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name,arguments:args})})).json();
    await fs.appendFile('E:/OpenAI-Codex/天皇のcodex/work/ab-marketing-20261103/browser-bridge-operations.jsonl',JSON.stringify({id,name,args,at:new Date().toISOString()})+'\n');
    while(true){const r=await(await fetch('http://127.0.0.1:8768/operation/'+id)).json();if(r.status==='complete')return r.result;if(r.status==='error')throw Error(r.error);await new Promise(r=>setTimeout(r,200));}
  };
  b.checkedTool=async(name,args={})=>{const r=await b.tool(name,args);const t=b.text(r);if(/^Error:|^Timed out|Failed to/i.test(t)||r.error||r.result?.isError)throw Error(t);return r;};
  b.snap=b.saveSnap=async(page,name)=>{const s=b.text(await b.checkedTool('take_snapshot',{pageId:page}));await fs.writeFile('E:/OpenAI-Codex/天皇のcodex/work/ab-marketing-20261103/'+name+'.txt',s);return s;};
  b.start=(name,args={})=>{const id=++b.seq;b.ops[id]={id,name,status:'pending'};b.tool(name,args).then(result=>Object.assign(b.ops[id],{status:'complete',result}),error=>Object.assign(b.ops[id],{status:'error',error:String(error)}));return{id,status:'pending'};};
  b.poll=id=>b.ops[id];
  b.namedUid=async(page,role,name)=>{const s=await b.saveSnap(page,'last-page-'+page);const rows=s.split('\n').filter(l=>l.includes(' '+role+' "'+name+'"')&&!l.includes('disableable disabled'));if(rows.length!==1)throw Error('Expected one '+role+' '+name+', found '+rows.length);return rows[0].match(/uid=([^\s]+)/)[1];};
  b.clickNamed=async(page,role,name)=>b.checkedTool('click',{pageId:page,uid:await b.namedUid(page,role,name)});
  b.typeUid=async(page,uid,value,submitKey='Tab')=>{await b.checkedTool('click',{pageId:page,uid});await b.checkedTool('press_key',{pageId:page,key:'Control+A'});await b.checkedTool('type_text',{pageId:page,text:String(value),submitKey});};
  b.inventoryReadFn="()=>[...document.querySelectorAll('[data-sku]')].map(e=>({sku:e.getAttribute('data-sku'),text:e.innerText,controls:[...e.querySelectorAll('kat-input')].map(i=>({value:i.value,label:i.getAttribute('label'),name:i.getAttribute('name')}))}))";
  return b;
}
