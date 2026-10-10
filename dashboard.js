"use strict";
(function(){
const $=id=>document.getElementById(id);
const samples={
 A:"You have been selected for a remote data entry job at Northstar Labs. Pay a $29 training deposit tonight through this link to reserve your position.",
 B:"Hello, I am a recruiter for Harbor Systems. We invite you to interview for a Software Engineering internship starting July 1. Please reply if interested.",
 C:"Your application has been approved. Send a passport scan and bank account details immediately before the interview."
};
const titles={overview:"Overview",inspect:"Inspect a message",evidence:"Evidence lab",response:"Response center"};
let evidence=[],assessment=null,latestInspection=null,crossReview=null,lastInspectedMessage="";
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
 evidence=[];assessment=null;crossReview=null;
 $("compare-output").hidden=true;$("consent-review").checked=false;$("evidence-log").replaceChildren();$("origin-list").replaceChildren();
 $("observation").value="";$("evidence-message").textContent="";renderGraph();
}
function showAnalysis(result){
 latestInspection=result;lastInspectedMessage=$("message").value.trim();resetEvidence();$("inspect-empty").hidden=true;$("results").hidden=false;
 const risky=result.status==="red_flag_observed";
 $("result-status").className="status"+(risky?" alert":"");
 $("result-title").textContent=risky?"Known warning signals detected":
   (result.ai_attention&&result.ai_attention.length?"Possible AI cautions — still unverified":"No listed flags — still unverified");
 $("result-detail").textContent=risky?"Pause and inspect the requests independently.":
   "A missing rule-based flag never establishes sender authenticity.";
 $("mode").className="mode"+(result.mode==="ai_extract"?"":" fallback");
 $("mode").textContent=result.mode==="ai_extract"?
    "● AI analysis active — source quotations and tentative cautions only.":
    "● Rules-only fallback — model unconfigured, unavailable or invalid.";
 $("claims").replaceChildren();
 if(Array.isArray(result.claims)&&result.claims.length){
  result.claims.forEach(c=>{
   const box=append($("claims"),"div","claim");
   append(box,"b","",c.category);
   append(box,"span","","“"+c.snippet+"”");
  });
 }else append($("claims"),"p","fine","No exact quote extracted; read the message itself.");
 $("flags").replaceChildren();
 if(Array.isArray(result.flag_explanations)&&result.flag_explanations.length){
  result.flag_explanations.forEach(f=>append($("flags"),"div","flag",f));
 }else append($("flags"),"p","fine","No simple pattern matched; this is not a safety verdict.");
 const cues=Array.isArray(result.ai_attention)?result.ai_attention:[];
 $("ai-checks").hidden=!cues.length;$("ai-signals").replaceChildren();
 cues.forEach(a=>{
  const box=append($("ai-signals"),"div","flag");
  append(box,"strong","",a.kind+": ");
  append(box,"span","","“"+a.snippet+"” — "+a.explanation+" (hypothesis only)");
 });
 $("caution").textContent=result.caution||"No authenticity verdict is available.";
 const questions=Array.isArray(result.verification_questions)?result.verification_questions:[];
 $("question-section").hidden=!questions.length;$("verification-questions").replaceChildren();
 questions.forEach((q,i)=>{
  const box=append($("verification-questions"),"div","question-card");
  append(box,"strong","","MISSION "+(i+1)+" · "+q.category);
  append(box,"div","question-quote","“"+q.quote+"”");
  append(box,"p","",q.question);
 });
 $("steps").replaceChildren();
 (result.next_steps||[]).forEach(s=>append($("steps"),"li","",s));
}
async function inspect(message,focus){
 const btn=$("analyze");btn.disabled=true;btn.textContent="Inspecting...";
 $("flash").textContent="";
 try{
  const result=await post("/api/analyze",{message});
  showAnalysis(result);
  if(focus)$("inspection-panel").scrollIntoView({behavior:"smooth",block:"start"});
  return true;
 }catch(e){$("flash").textContent="Inspection failed: "+e.message;return false;}
 finally{btn.disabled=false;btn.textContent="Inspect claims ↗";}
}
$("analyze").addEventListener("click",async()=>{
 const message=$("message").value.trim();
 if(!message){$("flash").textContent="Enter a message or select a fictional scenario.";return;}
 await inspect(message,true);
});
const demoNotes=[
 {kind:"other",source:"message",observation:"The recruiter supplied a link claiming to display this vacancy."},
 {kind:"company_careers",source:"independent",derived_from:[0],observation:"A polished vacancies page appears, but it was reached from that recruiter's link."},
 {kind:"company_contact",source:"independent",observation:"A separately located company channel described a Data Analyst internship beginning in August, unlike the stated Software Engineering internship."},
 {kind:"other",source:"independent",derived_from:[1,2],observation:"A comparison note mixing the recruiter-linked page and separately located channel."}
];
$("run-demo").addEventListener("click",async()=>{
 const b=$("run-demo");b.disabled=true;b.textContent="Investigating...";
 $("message").value=samples.B;$("count").textContent=samples.B.length+" / 12000";
 try{
  const good=await inspect(samples.B,false);
  if(!good){go("inspect");return;}
  assessment=await post("/api/assess",{evidence:demoNotes});
  evidence=demoNotes.map(x=>({...x}));renderGraph();renderNotes();
  go("evidence");$("collapse-notice").focus();
 }catch(e){go("evidence");$("evidence-message").textContent="Demo failed: "+e.message;}
 finally{b.disabled=false;b.textContent="Run full evidence demo ↗";}
});
function renderGraph(){
 const data=assessment||{nodes:[],edges:[],source_collapses:[],accepted_evidence:[]};
 window.OfferProofGraph.render($("graph"),data);
 const collapsed=data.source_collapses||[];
 $("evidence-summary").textContent=(data.accepted_evidence||[]).length+
   " independently sourced observation(s) reported · "+collapsed.length+
   " source collapse(s). No source or sender authenticated.";
 $("collapse-notice").className="notice"+(collapsed.length?" danger":"");
 $("collapse-notice").setAttribute("tabindex","-1");
 $("collapse-notice").textContent=collapsed.length?
  "Source collapse detected. The red node traces through one or more inputs controlled by the original sender or AI. This is NOT independent corroboration.":
  evidence.length?"No reported circular dependency. Even an independently found page may be fake; sender is unverified.":
  "No observations yet. Load the synthetic example to see real directed dependency edges.";
}
function renderNotes(){
 const ul=$("evidence-log");ul.replaceChildren();
 evidence.forEach((item,i)=>{
  const status=assessment?.nodes?.[i]?.classification||"unknown";
  const li=append(ul,"li",status==="source_collapse"?"bad":"");
  append(li,"strong","",status==="source_collapse"?"Source collapse · dependent":
         status==="dependent"?"Dependent on untrusted origin":"Separately sourced (self-reported)");
  append(li,"span","",item.observation);
 });
 const origins=$("origin-list");origins.replaceChildren();
 if(!evidence.length){append(origins,"span","fine","No earlier observations");return;}
 evidence.forEach((item,i)=>{
  const wrapper=append(origins,"label","dependency-option");
  const input=append(wrapper,"input");
  input.type="checkbox";input.value=String(i);
  append(wrapper,"span","","Observation "+(i+1)+" · "+item.observation.slice(0,46));
 });
}
$("record").addEventListener("click",async()=>{
 if(evidence.length>=10){$("evidence-message").textContent="Maximum 10 observations per trail.";return;}
 const observation=$("observation").value.trim();
 if(!observation){$("evidence-message").textContent="Enter a short observation first.";return;}
 const item={kind:$("kind").value,source:$("source").value,observation};
 const parents=Array.from($("origin-list").querySelectorAll("input:checked"),c=>Number(c.value));
 if(parents.length)item.derived_from=parents;
 const b=$("record");b.disabled=true;$("evidence-message").textContent="";
 try{assessment=await post("/api/assess",{evidence:evidence.concat(item)});evidence.push(item);crossReview=null;$("compare-output").hidden=true;renderGraph();renderNotes();$("observation").value="";}
 catch(e){$("evidence-message").textContent="Could not record: "+e.message;}
 finally{b.disabled=false;}
});
$("load-evidence-demo").addEventListener("click",async()=>{
 const demo=demoNotes;
 const b=$("load-evidence-demo");b.disabled=true;$("evidence-message").textContent="";
 try{assessment=await post("/api/assess",{evidence:demo});evidence=demo;crossReview=null;$("compare-output").hidden=true;renderGraph();renderNotes();}
 catch(e){$("evidence-message").textContent="Could not load sample: "+e.message;}
 finally{b.disabled=false;}
});
$("compare-case").addEventListener("click",async()=>{
 $("compare-message").textContent="";
 if(!$("consent-review").checked){
  $("compare-message").textContent="Confirm that you understand the external-AI data-sharing notice.";return;
 }
 if(!latestInspection || !$("message").value.trim() ||
    $("message").value.trim()!==lastInspectedMessage){
  $("compare-message").textContent="Inspect the current message first to link the evidence to this case.";return;
 }
 if(!evidence.length){
  $("compare-message").textContent="Add at least one user-reported observation before comparing.";return;
 }
 const b=$("compare-case");b.disabled=true;b.textContent="Comparing...";
 try{
  const result=await post("/api/compare",{message:lastInspectedMessage,evidence});
  crossReview=result;$("compare-output").hidden=false;
  const active=result.mode==="ai_compare";
  $("compare-mode").className="mode"+(active?"":" fallback");
  $("compare-mode").textContent=active?
   "● AI compared the two user-supplied text sets. All findings are hypotheses.":
   "● AI unavailable or invalid: no semantic comparison was completed.";
  $("comparison-list").replaceChildren();
  if(active && result.comparisons.length){
   result.comparisons.forEach((item,i)=>{
    const card=append($("comparison-list"),"div","comparison-card");
    append(card,"strong","","POSSIBLE DISCREPANCY "+(i+1)+" · "+item.kind);
    append(card,"div","question-quote","Message: “"+item.claim_quote+"”");
    append(card,"div","question-quote","Observation "+(item.note_index+1)+": “"+item.note_quote+"”");
    append(card,"p","",item.question);
    append(card,"span","fine","","Source status: "+item.note_classification+
      ". This is an unverified comparison, not an authenticity finding.");
   });
  }else append($("comparison-list"),"p","fine",active?
   "No quote-grounded textual discrepancy returned. This does not indicate authenticity.":
   "The graph remains available without AI; no model findings were produced.");
 }catch(e){$("compare-message").textContent="Comparison unavailable: "+e.message;}
 finally{b.disabled=false;b.textContent="Compare claims & observations ↗";}
});
$("download-case").addEventListener("click",()=>{
 const safe=x=>String(x||"").replace(/[\u0000-\u001f]+/g," ").trim();
 const lines=["OFFERPROOF — INVESTIGATION NOTE",
 "This is a user-reported evidence worksheet. Nothing below authenticates a sender.",
 "Date: "+new Date().toISOString(),
 "",
 "Inspection mode: "+safe(latestInspection?.mode||"not performed"),
 "Rule-based signals: "+safe((latestInspection?.red_flags||[]).join(", ")||"none listed"),
 "AI cautions (hypotheses only):",
 ...(latestInspection?.ai_attention||[]).map(a=>"- "+safe(a.kind)+" — "+safe(a.snippet)),
 "",
 "Claim excerpts (untrusted quotes):",
 ...(latestInspection?.claims||[]).map(c=>"- "+safe(c.category)+": "+safe(c.snippet)),
 "",
 "AI comparisons (unverified hypotheses):",
 ...(crossReview?.comparisons||[]).map(item=>"- "+safe(item.kind)+": "+
    safe(item.claim_quote)+" <> "+safe(item.note_quote)+
    " | provenance "+safe(item.note_classification)),
 "",
 "Questions for independent checking:",
 ...(latestInspection?.verification_questions||[]).map(q=>"- "+safe(q.question)),
 "",
 "Reported evidence:",
 ...evidence.map((item,i)=>"- Observation "+(i+1)+": "+safe(item.observation)+
   " | origin: "+safe(item.source)+" | dependencies: "+
   (Array.isArray(item.derived_from)?item.derived_from.map(n=>n+1).join(","):item.derived_from!==undefined?item.derived_from+1:"none")+
   " | classification: "+safe(assessment?.nodes?.[i]?.classification||"not assessed")),
 "",
 "CONCLUSION: Source authenticity and sender identity are NOT established.",
 "Do not follow unverified contact details; find an independent company channel."
 ];
 const text=lines.join("\n"),blob=new Blob([text],{type:"text/plain;charset=utf-8"});
 const url=URL.createObjectURL(blob),a=document.createElement("a");
 a.href=url;a.download="OfferProof-investigation.txt";document.body.appendChild(a);a.click();a.remove();
 setTimeout(()=>URL.revokeObjectURL(url),1500);
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
