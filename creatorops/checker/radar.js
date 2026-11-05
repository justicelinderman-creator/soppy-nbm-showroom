/* Cosie Release Radar UI. Browser-only local file handling; no upload endpoint. */
(() => {
  "use strict";
  const api=window.CosieRadarEngine;
  const $=id=>document.getElementById(id);
  let current=null,selection=0;
  function text(tag,style,value){
    const el=document.createElement(tag);
    if(style)el.className=style;
    el.textContent=String(value);
    return el;
  }
  function status(message,isError=false){
    $("status").textContent=message;
    $("status").classList.toggle("error",isError);
  }
  function beginSelection(){
    selection++;
    current=null;
    $("results").hidden=true;
    return selection;
  }
  function reset(){
    beginSelection();
    $("placeFile").value="";
    $("filter").value="ALL";
    $("search").value="";
    status("Ready. No file has been read.");
  }
  function show(report){
    current=report;
    $("results").hidden=false;
    $("metricObjects").textContent=report.counts.instances.toLocaleString();
    $("metricParts").textContent=report.counts.parts.toLocaleString();
    $("metricScripts").textContent=report.counts.scripts.toLocaleString();
    $("metricFindings").textContent=Object.values(report.severityTotals).reduce((a,b)=>a+b,0).toLocaleString();
    $("reportMeta").textContent=report.sourceLabel+" · "+report.counts.prompts+" prompts, "+report.counts.particles+" emitters, "+
      report.counts.lights+" lights. "+(report.findingsOmitted?report.findingsOmitted+" additional findings omitted due to display limit.":"All findings displayed.");
    $("filter").value="ALL";$("search").value="";
    renderFindings();
    status("Analysis finished locally. Your original file was not changed or uploaded.");
  }
  function renderFindings(){
    if(!current)return;
    const severity=$("filter").value,query=$("search").value.trim().toLowerCase();
    const matches=current.findings.filter(f=>(severity==="ALL"||f.severity===severity)&&
      (!query||(f.path+" "+f.rule+" "+f.detail).toLowerCase().includes(query)));
    const list=$("findings");
    list.replaceChildren();
    for(const f of matches){
      const item=document.createElement("li");
      item.className="finding";item.dataset.severity=f.severity;
      item.append(text("div","minor",f.severity+" · "+f.rule+" · "+f.className),
                  text("h3","",f.path),text("p","",f.detail),text("p","minor","CHECK: "+f.action));
      list.appendChild(item);
    }
    $("findingCount").textContent=matches.length+" of "+current.findings.length+" displayed findings"+
      (current.findingsOmitted?"; "+current.findingsOmitted+" other findings omitted.":".")+
      (matches.length?"":" No matching findings.");
  }
  async function openFile(file){
    if(!file)return;
    const request=beginSelection();
    if(!/\.(rbxlx|rbxmx)$/i.test(file.name||""))return failure("Use .rbxlx/.rbxmx XML, not binary .rbxl/.rbxm.");
    if(file.size<=0 || file.size>api.maxBytes)return failure("The file is empty or exceeds the 12 MB browser limit.");
    status("Inspecting the selected XML inside this tab…");
    try {
      const xml=await file.text();
      // A newer selection, demo or Clear owns the display and export now.
      if(request!==selection)return;
      show(api.analyze(xml,file.name));
    }
    catch(error){if(request===selection)failure(error.message||"File could not be inspected.");}
  }
  function failure(message){current=null;$("results").hidden=true;status(message,true);}
  function download(){
    if(!current)return;
    const file=new Blob([JSON.stringify(current,null,2)+"\n"],{type:"application/json"});
    const url=URL.createObjectURL(file);
    const link=document.createElement("a");
    link.href=url;link.download="cosie-release-radar-report.json";
    document.body.appendChild(link);link.click();link.remove();
    setTimeout(()=>URL.revokeObjectURL(url),1000);
  }
  const demo='<?xml version="1.0"?><roblox version="4"><Item class="Workspace"><Properties><string name="Name">Workspace</string></Properties>'+
    '<Item class="Part"><Properties><string name="Name">Invisible Collider</string><bool name="CanCollide">true</bool><float name="Transparency">1</float><bool name="Anchored">true</bool></Properties></Item>'+
    '<Item class="Part"><Properties><string name="Name">Large Loose Wall</string><bool name="Anchored">false</bool><Vector3 name="Size"><X>50</X><Y>12</Y><Z>2</Z></Vector3></Properties></Item>'+
    '<Item class="ProximityPrompt"><Properties><string name="Name">Blocked Prompt</string><bool name="Enabled">true</bool><float name="MaxActivationDistance">0</float></Properties></Item>'+
    '<Item class="ParticleEmitter"><Properties><string name="Name">Busy Sparks</string><bool name="Enabled">true</bool><float name="Rate">240</float></Properties></Item>'+
    '<Item class="PointLight"><Properties><string name="Name">Wide Light</string><bool name="Enabled">true</bool><float name="Range">60</float><float name="Brightness">9</float></Properties></Item>'+
    '<Item class="ModuleScript"><Properties><string name="Name">Example Script</string></Properties></Item>'+
    '</Item></roblox>';
  $("placeFile").addEventListener("change",e=>openFile(e.target.files?.[0]));
  $("demo").addEventListener("click",()=>{
    beginSelection();
    try {show(api.analyze(demo,"Synthetic example — not a real game"));}
    catch(err){failure(err.message||"Demo failed");}
  });
  $("reset").addEventListener("click",reset);
  $("filter").addEventListener("change",renderFindings);
  $("search").addEventListener("input",renderFindings);
  $("download").addEventListener("click",download);
  const drop=$("drop");
  for(const name of ["dragenter","dragover"])drop.addEventListener(name,e=>{e.preventDefault();drop.classList.add("is-over");});
  for(const name of ["dragleave","drop"])drop.addEventListener(name,e=>{e.preventDefault();drop.classList.remove("is-over");});
  drop.addEventListener("drop",e=>openFile(e.dataTransfer?.files?.[0]));
  drop.addEventListener("keydown",e=>{
    if(e.target===drop&&(e.key==="Enter"||e.key===" ")){e.preventDefault();$("placeFile").click();}
  });
})();
