/* Regression fixture only. No test hooks are installed in the production page. */
(() => {
  'use strict';
  const $=id=>document.getElementById(id);
  const params=new URLSearchParams(location.search);
  const target=params.get('baseline')==='1'?'../../baseline/creatorops/checker/index.html':'../creatorops/checker/index.html';
  const XML='<roblox version="4"><Item class="Part"><Properties><string name="Name">Synthetic invisible collider</string><bool name="CanCollide">true</bool><float name="Transparency">1</float></Properties></Item></roblox>';
  const settle=()=>new Promise(resolve=>setTimeout(resolve,0));
  function assert(condition,message){if(!condition)throw Error(message);}
  async function fixture(){
    const frame=document.createElement('iframe');frame.title='Isolated synthetic checker fixture';
    const loaded=new Promise((resolve,reject)=>{frame.onload=resolve;frame.onerror=reject;});
    frame.src=target;$('fixture').replaceChildren(frame);await loaded;
    const w=frame.contentWindow,d=w.document,by=id=>d.getElementById(id),blobs=[],errors=[];
    assert(!!w.CosieRadarEngine,'Checker engine did not load');
    w.addEventListener('error',e=>errors.push(e.message));
    w.addEventListener('unhandledrejection',e=>errors.push(String(e.reason)));
    const nativeCreate=w.URL.createObjectURL.bind(w.URL);
    w.URL.createObjectURL=blob=>{blobs.push(blob);return nativeCreate(blob);};
    d.addEventListener('click',e=>{if(e.target.closest('a[download]'))e.preventDefault();},true);
    function select(file,route='change'){
      const transfer=new w.DataTransfer();if(file)transfer.items.add(file);
      if(route==='drop')by('drop').dispatchEvent(new w.DragEvent('drop',{dataTransfer:transfer,bubbles:true}));
      else {by('placeFile').files=transfer.files;by('placeFile').dispatchEvent(new w.Event('change',{bubbles:true}));}
    }
    function pending(name='slow.rbxlx',route='change'){
      let resolve,reject;
      const promise=new Promise((yes,no)=>{resolve=yes;reject=no;});
      const file=new w.File([XML],name,{type:'application/xml'});
      Object.defineProperty(file,'text',{value:()=>promise});select(file,route);
      return {resolve:(value=XML)=>resolve(value),reject:()=>reject(new Error('Synthetic read failed'))};
    }
    async function real(name='latest.rbxlx',content=XML){
      select(new w.File([content],name,{type:'application/xml'}));
      const deadline=performance.now()+5000;
      while(by('status').textContent.startsWith('Inspecting')&&performance.now()<deadline)await new Promise(resolve=>setTimeout(resolve,10));
      assert(!by('status').textContent.startsWith('Inspecting'),'Native File.text did not settle within five seconds');
    }
    function shown(name){return !by('results').hidden&&by('reportMeta').textContent.startsWith(name+' ·');}
    async function report(){blobs.length=0;by('download').click();return blobs.length?JSON.parse(await blobs[0].text()):null;}
    return {w,d,by,blobs,errors,select,pending,real,shown,report,close:()=>frame.remove()};
  }
  const cases=[
    ['Clear cancels a late successful read',async f=>{const a=f.pending();f.by('reset').click();a.resolve();await settle();assert(f.by('results').hidden&&f.by('status').textContent==='Ready. No file has been read.','Cleared report returned');assert(await f.report()===null,'Cleared report downloadable');}],
    ['Clear ignores a late read error',async f=>{const a=f.pending();f.by('reset').click();a.reject();await settle();assert(f.by('status').textContent==='Ready. No file has been read.','Late error replaced Clear');}],
    ['Newest successful selection wins',async f=>{const a=f.pending('older.rbxlx');await f.real();a.resolve();await settle();assert(f.shown('latest.rbxlx'),'Older read replaced newer report');assert((await f.report()).sourceLabel==='latest.rbxlx','Export belongs to wrong file');}],
    ['Older read error cannot hide newer report',async f=>{const a=f.pending();await f.real();a.reject();await settle();assert(f.shown('latest.rbxlx'),'Old error hid newer report');}],
    ['Newest read error remains authoritative',async f=>{const a=f.pending('old.rbxlx'),b=f.pending('new.rbxlx');b.reject();await settle();a.resolve();await settle();assert(f.by('results').hidden&&f.by('status').textContent==='Synthetic read failed','Old success hid newer failure');}],
    ['Invalid extension supersedes earlier read',async f=>{const a=f.pending();await f.real('binary.rbxl');a.resolve();await settle();assert(f.by('results').hidden&&f.by('status').textContent.includes('not binary'),'Invalid selection replaced by old success');}],
    ['Malformed XML supersedes earlier read',async f=>{const a=f.pending();await f.real('broken.rbxlx','<broken>');a.resolve();await settle();assert(f.by('results').hidden&&f.by('status').classList.contains('error'),'Old success replaced malformed XML error');}],
    ['Demo supersedes earlier successful read',async f=>{const a=f.pending();f.by('demo').click();a.resolve();await settle();assert(f.shown('Synthetic example — not a real game'),'Old file replaced demo');}],
    ['Demo survives earlier read error',async f=>{const a=f.pending();f.by('demo').click();a.reject();await settle();assert(f.shown('Synthetic example — not a real game'),'Old error removed demo');}],
    ['Pending selection hides the previous report and export',async f=>{await f.real();const a=f.pending();assert(f.by('results').hidden,'Old report remains visible while another is loading');assert(await f.report()===null,'Old report remains exportable');a.resolve();await settle();}],
    ['Dropping a second file supersedes a pending selection',async f=>{const a=f.pending('input.rbxlx'),b=f.pending('drop.rbxmx','drop');b.resolve();await settle();a.resolve();await settle();assert(f.shown('drop.rbxmx'),'Old input replaced newer dropped file');}],
    ['Selecting a second file supersedes a pending drop',async f=>{const a=f.pending('drop.rbxmx','drop');await f.real();a.resolve();await settle();assert(f.shown('latest.rbxlx'),'Old drop replaced newer input');}],
    ['Clear invalidates multiple pending reads',async f=>{const a=f.pending('a.rbxlx'),b=f.pending('b.rbxlx');f.by('reset').click();b.resolve();a.reject();await settle();assert(f.by('results').hidden&&f.by('status').textContent==='Ready. No file has been read.','A queued result survived Clear');}],
    ['An empty chooser event leaves current report intact',async f=>{await f.real();f.select(null);await settle();assert(f.shown('latest.rbxlx'),'Empty chooser changed report');}],
    ['Actual File.text and downloaded JSON agree',async f=>{await f.real('real-file.rbxmx');assert(f.shown('real-file.rbxmx'),'Ordinary file did not load');const r=await f.report();assert(r.sourceLabel==='real-file.rbxmx'&&r.counts.parts===1&&r.findings[0].rule==='INVISIBLE_SOLID','Report mismatch');}],
    ['Current read failure clears previous result',async f=>{await f.real();const a=f.pending();a.reject();await settle();assert(f.by('results').hidden&&f.by('status').textContent==='Synthetic read failed','Current failure not shown');assert(await f.report()===null,'Failed read permits prior export');}],
    ['Current malformed XML is rejected',async f=>{await f.real('bad.rbxlx','<not-roblox/>');assert(f.by('results').hidden&&f.by('status').classList.contains('error'),'Invalid XML accepted');}],
    ['Empty and oversized inputs are rejected before reading',async f=>{for(const size of [0,12*1024*1024+1]){let read=false;const file=new f.w.File(['x'],'sized.rbxlx');Object.defineProperties(file,{size:{value:size},text:{value:()=>{read=true;return Promise.resolve(XML);}}});f.select(file);await settle();assert(!read&&f.by('results').hidden&&f.by('status').textContent.includes('empty or exceeds'),'Size guard failed');}}],
    ['Filtering and search still operate after selection',async f=>{await f.real();f.by('filter').value='HIGH';f.by('filter').dispatchEvent(new f.w.Event('change'));assert(f.by('findings').children.length===0,'Severity filter failed');f.by('filter').value='ALL';f.by('filter').dispatchEvent(new f.w.Event('change'));f.by('search').value='collider';f.by('search').dispatchEvent(new f.w.Event('input'));assert(f.by('findings').children.length===1,'Text filter failed');}],
    ['Raw script source stays out of display and export',async f=>{await f.real('private_synthetic.rbxlx','<roblox><Item class="ModuleScript"><Properties><string name="Name">Synthetic module</string><ProtectedString name="Source">PRIVATE_SYNTHETIC_CANARY</ProtectedString></Properties></Item></roblox>');assert(!f.d.body.textContent.includes('PRIVATE_SYNTHETIC_CANARY')&&!JSON.stringify(await f.report()).includes('PRIVATE_SYNTHETIC_CANARY'),'Script source leaked');}]
  ];
  $('run').addEventListener('click',async()=>{
    $('run').disabled=true;$('checks').replaceChildren();$('receipt').textContent='';const checks=[];
    for(const [name,fn] of cases){let f;const row={name,pass:false};
      try{f=await fixture();await fn(f);assert(f.errors.length===0,'Browser errors: '+f.errors.join('; '));row.pass=true;}
      catch(error){row.error=String(error.message||error);}
      finally{if(f)f.close();}
      checks.push(row);const li=document.createElement('li');li.className=row.pass?'pass':'fail';li.textContent=(row.pass?'PASS: ':'FAIL: ')+name+(row.error?' — '+row.error:'');$('checks').append(li);
    }
    const receipt={target,at_utc:new Date().toISOString(),total:checks.length,passed:checks.filter(c=>c.pass).length,checks,
      method:'Real browser DOM and checker engine; deferred synthetic File.text for races; native File.text for ordinary loading; captured JSON Blob exports',customer_files_used:false,network_uploads:0,published:false};
    $('summary').textContent=receipt.passed+' / '+receipt.total+' passed';$('receipt').textContent=JSON.stringify(receipt,null,2);$('run').disabled=false;
  });
})();
