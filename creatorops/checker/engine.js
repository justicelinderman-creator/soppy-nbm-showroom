/* Cosie Release Radar: offline-only XML inspection, no network or storage. */
(() => {
  "use strict";
  const partTypes = new Set(["Part","WedgePart","CornerWedgePart","MeshPart","UnionOperation","SpawnLocation","TrussPart","Seat","VehicleSeat"]);
  const scriptTypes = new Set(["Script","LocalScript","ModuleScript"]);
  const lightTypes = new Set(["PointLight","SpotLight","SurfaceLight"]);
  const rank = {HIGH:0,MEDIUM:1,INFO:2};
  const children = el => el ? Array.from(el.children) : [];
  const child = (el,tag) => children(el).find(x=>x.tagName===tag) || null;
  const property = (item,key) => children(child(item,"Properties")).find(x=>x.getAttribute("name")===key) || null;
  const value = el => el ? String(el.textContent||"").trim() : null;
  const number = el => {const text=value(el);const n=Number(text);return text!==null&&text!==""&&Number.isFinite(n)?n:null;};
  const boolean = el => {const s=value(el);return s==="true"?true:s==="false"?false:null;};
  const vector = el => {
    if(!el)return null;
    const x=number(child(el,"X")),y=number(child(el,"Y")),z=number(child(el,"Z"));
    return [x,y,z].every(n=>n!==null)?{x,y,z}:null;
  };
  const label = item => (value(property(item,"Name")) || item.getAttribute("class") || "Instance").slice(0,90).replace(/[\r\n\t]/g," ");
  function path(item){
    const bits=[];
    for(let node=item,depth=0;node&&depth<14;node=node.parentElement,depth++){
      if(node.tagName==="Item")bits.push(label(node));
    }
    return bits.reverse().join(" / ");
  }
  function analyze(xml,source="Local XML file"){
    if(typeof xml!=="string" || xml.length>12*1024*1024)throw Error("Invalid file or over 12 MB.");
    if(/<!\s*(DOCTYPE|ENTITY)\b/i.test(xml))throw Error("XML entity declarations are not supported.");
    const doc=new DOMParser().parseFromString(xml,"application/xml");
    if(doc.documentElement.tagName!=="roblox" || doc.querySelector("parsererror"))throw Error("Not a valid Roblox XML place/model.");
    const items=doc.getElementsByTagName("Item");
    if(!items.length || items.length>60000)throw Error("This file does not contain a supported scene size.");
    const counts={instances:items.length,parts:0,scripts:0,prompts:0,particles:0,lights:0},totals={HIGH:0,MEDIUM:0,INFO:0},findings=[];
    function add(rule,severity,item,detail,action){
      totals[severity]++;
      if(findings.length<180)findings.push({rule,severity,path:path(item),className:item.getAttribute("class")||"Unknown",detail,action});
    }
    for(const item of items){
      const cls=item.getAttribute("class")||"";
      if(scriptTypes.has(cls)){counts.scripts++;continue;}
      if(partTypes.has(cls)){
        counts.parts++;
        const collision=boolean(property(item,"CanCollide")),transparent=number(property(item,"Transparency"));
        const size=vector(property(item,"Size")),anchored=boolean(property(item,"Anchored"));
        if(collision===true && transparent!==null && transparent>=0.97)add("INVISIBLE_SOLID","MEDIUM",item,
          "Almost invisible part has collision enabled; intentional hitboxes can look like this.",
          "Review CanCollide and test movement in Studio.");
        if(size && [size.x,size.y,size.z].some(n=>n<=0))add("INVALID_SIZE","HIGH",item,
          "A saved dimension is zero or negative.","Inspect the original Size property.");
        else if(size && anchored===false && (size.x*size.y*size.z>=350||Math.max(size.x,size.y,size.z)>=40))
          add("LARGE_UNANCHORED","MEDIUM",item,"Large geometry is unanchored.","Check intended physics behavior; test before changing it.");
      }else if(cls==="ProximityPrompt"){
        counts.prompts++;
        const enabled=boolean(property(item,"Enabled")),dist=number(property(item,"MaxActivationDistance"));
        if(enabled!==false && dist!==null && dist<=0)add("PROMPT_ZERO_RANGE","HIGH",item,
          "Prompt has zero or negative interaction distance.","Set a meaningful range if this interaction should be usable.");
      }else if(cls==="ParticleEmitter"){
        counts.particles++;
        const enabled=boolean(property(item,"Enabled")),rate=number(property(item,"Rate"));
        if(enabled===true && rate!==null && rate>=200)add("PARTICLE_HIGH_RATE","MEDIUM",item,
          "Enabled emitter rate is "+rate+" per second.","Measure effect cost on real target devices.");
      }else if(lightTypes.has(cls)){
        counts.lights++;
        const enabled=boolean(property(item,"Enabled")),range=number(property(item,"Range")),bright=number(property(item,"Brightness"));
        if(enabled===true && range!==null && bright!==null && range>=60 && bright>=5)
          add("WIDE_BRIGHT_LIGHT","INFO",item,"Wide and bright light settings may be intentional.","Inspect visual intent and profile on device.");
      }
    }
    findings.sort((a,b)=>rank[a.severity]-rank[b.severity]||a.path.localeCompare(b.path));
    return {format:"cosie.release-radar.v1",origin:"LOCAL_BROWSER_ONLY",sourceLabel:String(source).slice(0,120),
      createdUtc:new Date().toISOString(),counts,severityTotals:totals,
      findingsShown:findings.length,findingsOmitted:Object.values(totals).reduce((a,b)=>a+b,0)-findings.length,
      limitations:"Advisory, static XML only; no script analysis, FPS test, or game mutation",findings};
  }
  window.CosieRadarEngine=Object.freeze({analyze,maxBytes:12*1024*1024});
})();
