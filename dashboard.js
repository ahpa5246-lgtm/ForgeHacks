"use strict";
(function(){
const $=id=>document.getElementById(id);
const samples={
 A:"You have been selected for a remote data entry job at Northstar Labs. Pay a $29 training deposit tonight through this link to reserve your position.",
 B:"Hello, I am a recruiter for Harbor Systems. We invite you to interview for an internship next week. Reply if interested.",
 C:"Your application has been approved. Send a passport scan and bank account details immediately before the interview."
};
const titles={overview:"Overview",inspect:"Inspect a message",evidence:"Evidence lab",response:"Response center"};
let evidence=[],assessment=null;
function el(tag,cls,str){const x=document.createElement(tag);if(cls)x.className=cls;if(str!==undefined)x.textContent=str;return x;}
function append(target,tag,cls,str){const x=el(tag,cls,str);target.appendChild(x);return x;}
function go(view){
 if(!titles[view])return;
 document.querySelectorAll(".view").forEach(x=>x.hidden=x.id!=="view-"+view);
 document.querySelectorAll(".nav button").forEach(x=>{
  const active=x.dataset.view===view;x.classList.toggle("active",active);
  if(active)x.setAttribute("aria-current","page");else x.removeAttribute("aria-current");
 });
 $("crumb").textContent=titles[view];
 if(window.history.replaceState)window.history.replaceState(null,"","#"+view);
 window.scrollTo({top:0,behavior:"instant"});
}
function sample(id){$("message").value=samples[id];$("count").textContent=$("message").value.length+" / 12000";$("flash").textContent="";go("inspect");$("message").focus();}
document.querySelectorAll("[data-view]").forEach(b=>b.addEventListener("click",()=>go(b.dataset.view)));
document.querySelectorAll("[data-go]").forEach(b=>b.addEventListener("click",()=>go(b.dataset.go)));
document.querySelectorAll("[data-sample]").forEach(b=>b.addEventListener("click",()=>sample(b.dataset.sample)));
$("brand").addEventListener("click",e=>{e.preventDefault();go("overview");});
$("overview-demo").addEventListener("click",()=>sample("B"));
$("message").addEventListener("input",()=>{$("count").textContent=$("message").value.length+" / 12000";});
async function post(path,payload){
 const controller=new AbortController();const timeout=setTimeout(()=>controller.abort(),18000);
 try{
  const res=await fetch(path,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload),signal:controller.signal});
  let data;try{data=await res.json();}catch(_){throw Error("Invalid response from the service.");}
  if(!res.ok)throw Error(data.error||("Request failed ("+res.status+")"));
  return data;
 }catch(e){if(e.name==="AbortError")throw Error("Request timed out. Retry or check the model quota.");throw e;}
 finally{clearTimeout(timeout);}
}
function resetEvidence(){
 evidence=[];assessment=null;$("evidence-log").replaceChildren();$("origin").replaceChildren(new Option("No earlier observation",""));
 $("observation").value="";$("evidence-message").textContent="";renderGraph();
}
$("analyze").addEventListener("click",async()=>{
 const message=$("message").value.trim();
 if(!message){$("flash").textContent="Enter a message or select a fictional scenario.";return;}
 $("flash").textContent="";const btn=$("analyze");btn.disabled=true;btn.textContent="Inspecting...";
 try{
  const result=await post("/api/analyze",{message});
  resetEvidence();$("inspect-empty").hidden=true;$("results").hidden=false;
  const alert=result.status==="red_flag_observed";
  $("result-status").className="status"+(alert?" alert":"");
  $("result-title").textContent=alert?"Warning signals detected":"No listed flags — still unverified";
  $("result-detail").textContent=alert?"Pause and inspect these risky requests independently.":"Missing red flags do not establish sender authenticity.";
  $("mode").className="mode"+(result.mode==="ai_extract"?"":" fallback");
  $("mode").textContent=result.mode==="ai_extract"?"● AI extraction active — exact quotes only, no AI verdicts.":"● Rules-only fallback — AI unavailable, unconfigured, or returned invalid data.";
  $("claims").replaceChildren();
  if(Array.isArray(result.claims)&&result.claims.length){
   result.claims.forEach(c=>{const box=append($("claims"),"div","claim");append(box,"b","",c.category);append(box,"span","","“"+c.snippet+"”");});
  }else append($("claims"),"p","fine","No exact quotes extracted. Review the message yourself.");
  $("flags").replaceChildren();
  if(Array.isArray(result.flag_explanations)&&result.flag_explanations.length){result.flag_explanations.forEach(f=>append($("flags"),"div","flag",f));}
  else append($("flags"),"p","fine","No matching pattern found. Scammers may use other wording.");
  $("ai-checks").hidden=!(Array.isArray(result.ai_attention)&&result.ai_attention.length);
  $("ai-signals").replaceChildren();
  (result.ai_attention||[]).forEach(a=>{
   const box=append($("ai-signals"),"div","flag","");
   append(box,"strong","",a.kind+": ");
   append(box,"span","","“"+a.snippet+"” — "+a.explanation);
  });
  $("caution").textContent=result.caution||"No authenticity verdict is available.";
  $("steps").replaceChildren();(result.next_steps||[]).forEach(s=>append($("steps"),"li","",s));
  $("inspection-panel").scrollIntoView({behavior:"smooth",block:"start"});
 }catch(e){$("flash").textContent="Inspection failed: "+e.message;}
 finally{btn.disabled=false;btn.textContent="Inspect claims ↗";}
});
function renderGraph(){
 const g=$("graph");g.replaceChildren();const origin=append(g,"div","graphnode");
 append(origin,"div","nlabel","Origin");append(origin,"strong","","Recruiter message · unverified");
 append(origin,"p","","No claim has been independently authenticated.");
 if(evidence.length===0){
  append(g,"p","graph-empty","Your source trail appears here after you add observations or load a fictional example.");
  $("collapse-notice").className="notice";
  $("collapse-notice").textContent="No observations yet. Try the fictional source-collapse example.";
  $("evidence-summary").textContent="0 independent observations recorded. No sender authenticated.";return;
 }
 const collapsed=assessment?assessment.source_collapses:[];
 evidence.forEach((item,i)=>{
  append(g,"div","connector",item.derived_from!==undefined?"↳ Derived from observation "+(item.derived_from+1):item.source==="independent"?"↳ Independently sourced (user reported)":"↳ From "+(item.source==="ai"?"AI suggestion":"recruiter message"));
  const bad=collapsed.includes(i);
  const box=append(g,"div","graphnode "+(bad?"collapse":"regular"));
  append(box,"div","nlabel",bad?"SOURCE COLLAPSE":item.source==="independent"?"SELF-REPORTED SOURCE":"DEPENDENT SOURCE");
  append(box,"strong","","Observation "+(i+1));
  append(box,"p","",item.observation);
 });
 const count=assessment?assessment.accepted_evidence.length:0;
 $("evidence-summary").textContent=count+" independently sourced observation(s) reported · "+collapsed.length+" collapsed chain(s) · 0 authenticated senders.";
 $("collapse-notice").className="notice"+(collapsed.length?" danger":"");
 $("collapse-notice").textContent=collapsed.length?"Source collapse detected. A record labeled independent actually depends on the original recruiter message or AI. It is not independent corroboration.":"No reported source collapse in this trail. Independently found pages can still be fake; sender remains unverified.";
}
function renderNotes(){
 const ul=$("evidence-log");ul.replaceChildren();
 evidence.forEach((item,i)=>{
  const bad=assessment&&assessment.source_collapses.includes(i);
  const li=append(ul,"li",bad?"bad":"");
  append(li,"strong","",bad?"Circular source detected":item.source==="independent"?"User-reported independent":"Dependent source");
  append(li,"span","",item.observation);
 });
 $("origin").replaceChildren(new Option("No earlier observation",""));
 evidence.forEach((item,i)=>$("origin").add(new Option("Observation "+(i+1)+" — "+item.observation.slice(0,32),String(i))));
 $("origin").value="";
}
$("record").addEventListener("click",async()=>{
 if(evidence.length>=10){$("evidence-message").textContent="Maximum 10 observations per trail.";return;}
 const observation=$("observation").value.trim();
 if(!observation){$("evidence-message").textContent="Enter a short observation first.";return;}
 const item={kind:$("kind").value,source:$("source").value,observation};
 if($("origin").value!=="")item.derived_from=Number($("origin").value);
 const b=$("record");b.disabled=true;$("evidence-message").textContent="";
 try{assessment=await post("/api/assess",{evidence:evidence.concat(item)});evidence.push(item);renderGraph();renderNotes();$("observation").value="";}
 catch(e){$("evidence-message").textContent="Could not record: "+e.message;}
 finally{b.disabled=false;}
});
$("load-evidence-demo").addEventListener("click",async()=>{
 const demo=[
 {kind:"other",source:"message",observation:"The recruiter supplied a link supposedly showing the job."},
 {kind:"company_careers",source:"independent",derived_from:0,observation:"The careers page looked legitimate, but I arrived through that link."},
 {kind:"company_contact",source:"independent",observation:"I found a company contact channel using a route unrelated to the message."}
 ];
 const b=$("load-evidence-demo");b.disabled=true;$("evidence-message").textContent="";
 try{assessment=await post("/api/assess",{evidence:demo});evidence=demo;renderGraph();renderNotes();}
 catch(e){$("evidence-message").textContent="Could not load sample: "+e.message;}
 finally{b.disabled=false;}
});
$("respond").addEventListener("click",async()=>{
 const events=Array.from(document.querySelectorAll(".event:checked"),e=>e.value);
 const b=$("respond");b.disabled=true;$("response-message").textContent="";
 try{
  const result=await post("/api/respond",{events});
  $("response-empty").hidden=true;$("response-output").hidden=false;$("response-steps").replaceChildren();
  (result.steps||[]).forEach(s=>append($("response-steps"),"li","",s));
 }catch(e){$("response-message").textContent="Could not generate recovery steps: "+e.message;}
 finally{b.disabled=false;}
});
async function health(){
 try{
  const r=await fetch("/health",{cache:"no-store"});
  if(!r.ok)throw Error();
  const state=await r.json();
  $("server-state").textContent=state.ai_configured?"AI key configured · test in inspection":"Rules-only · AI key not configured";
 }catch(_){$("server-state").textContent="Service status unknown";}
}
const selected=location.hash.slice(1);go(titles[selected]?selected:"overview");renderGraph();health();
})();
