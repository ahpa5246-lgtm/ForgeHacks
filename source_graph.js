"use strict";
/* An actual directed acyclic evidence graph. SVG is DOM-built, never HTML-injected. */
window.OfferProofGraph = (function () {
  const NS = "http://www.w3.org/2000/svg";
  const palette = {
    ink:"#24384b", muted:"#647c8f", line:"#9aaebd",
    root:"#23364f", dependent:"#fff4e8", collapse:"#ffecf0",
    independent:"#e5f6f1", red:"#b3485b", green:"#087f75"
  };
  function shape(parent, tag, attrs, content) {
    const element = document.createElementNS(NS,tag);
    for(const [k,v] of Object.entries(attrs||{}))element.setAttribute(k,String(v));
    if(content!==undefined)element.textContent=content;
    parent.appendChild(element);
    return element;
  }
  function label(parent, value,x,y,opts={}) {
    return shape(parent,"text",{
      x,y,fill:opts.fill||palette.ink,
      "font-family":"Inter,ui-sans-serif,system-ui,sans-serif",
      "font-size":opts.size||14,
      "font-weight":opts.weight||600,
      "text-anchor":opts.anchor||"start"
    }, value);
  }
  function words(text,max=37,lines=3) {
    const parts=String(text).split(/\s+/), result=[];
    let line="";
    for(const part of parts) {
      if((line+" "+part).trim().length>max && line) {
        result.push(line);line=part;
      }else line=(line+" "+part).trim();
      if(result.length===lines)break;
    }
    if(result.length<lines&&line)result.push(line);
    if(result.join(" ").length<String(text).length) {
      result[result.length-1]=result[result.length-1].slice(0,max-1)+"…";
    }
    return result;
  }
  function render(container,data) {
    container.replaceChildren();
    const svg=shape(container,"svg",{
      viewBox:"0 0 790 "+(data.nodes.length?235+Math.ceil(data.nodes.length/2)*176:265),
      role:"img",
      "aria-label":"Directed evidence graph. Blue nodes denote original untrusted message or AI; red nodes show circular evidence; green denotes separately sourced, but not authenticated, observations.",
      class:"evidence-svg"
    });
    const defs=shape(svg,"defs");
    [["arrow","#91a9bb"],["arrow-red",palette.red]].forEach(([id,color])=>{
      const marker=shape(defs,"marker",{id,markerWidth:8,markerHeight:8,refX:7,refY:3,orient:"auto",markerUnits:"strokeWidth"});
      shape(marker,"path",{d:"M0 0L7 3L0 6",fill:"none",stroke:color,"strokeWidth":"1.6"});
    });
    const points={
      message:{x:220,y:82}, ai:{x:570,y:82}
    };
    for(const n of data.nodes)points[n.id]={x:n.id%2?570:220,y:250+Math.floor(n.id/2)*176};
    // Draw all links behind nodes; this is not a fake linear connector list.
    const edgeGroup=shape(svg,"g",{});
    for(const e of data.edges) {
      const from=points[e.from],to=points[e.to];
      if(!from||!to)continue;
      const sameRow=Math.abs(from.y-to.y)<2;
      let d;
      if(sameRow) {
        const dir=to.x>from.x?1:-1;
        d="M "+(from.x+dir*145)+" "+from.y+" C "+(from.x+dir*210)+" "+(from.y-100)+" "+(to.x-dir*210)+" "+(to.y-100)+" "+(to.x-dir*145)+" "+to.y;
      }else{
        const sy=from.y+46,ty=to.y-47;
        const mid=(sy+ty)/2;
        d="M "+from.x+" "+sy+" C "+from.x+" "+mid+" "+to.x+" "+mid+" "+to.x+" "+ty;
      }
      const tainted=(e.from==="message"||e.from==="ai"||
           (typeof e.from==="number"&&data.nodes[e.from]?.tainted_by.length));
      const red=Boolean(tainted);
      shape(edgeGroup,"path",{
        d,stroke:red?palette.red:palette.line,
        fill:"none","stroke-width":red?2.5:1.8,
        "stroke-dasharray":e.relation==="origin"?"6 5":"none",
        "marker-end":red?"url(#arrow-red)":"url(#arrow)"
      });
    }
    function box(key,title,desc,variant,note) {
      const p=points[key],w=291,h=94;
      const colors=variant==="root"?[palette.root,"#eef7fa","#b3d5e4"]:
                   variant==="collapse"?[palette.collapse,palette.ink,palette.red]:
                   variant==="dependent"?[palette.dependent,palette.ink,"#996230"]:
                   [palette.independent,palette.ink,palette.green];
      const group=shape(svg,"g",{});
      shape(group,"rect",{x:p.x-w/2,y:p.y-h/2,width:w,height:h,rx:11,fill:colors[0],
                            stroke:variant==="root"?"#57748e":colors[2],
                            "stroke-width":variant==="collapse"?2.3:1.1});
      label(group,title,p.x-w/2+15,p.y-h/2+24,{fill:colors[1],size:14,weight:800});
      const lines=words(desc,43,2);
      lines.forEach((line,i)=>label(group,line,p.x-w/2+15,p.y-h/2+49+i*17,{
        fill:variant==="root"?"#bcd2e1":palette.muted,size:11,weight:500
      }));
      if(note)label(group,note,p.x+w/2-12,p.y-h/2+23,{
        fill:variant==="root"?"#92d9c8":colors[2],size:9,weight:800,anchor:"end"
      });
      shape(group,"title",{},desc);
    }
    box("message","Recruiter message","Unverified sender-controlled origin","root","ORIGIN");
    box("ai","AI suggestion","Untrusted generated output","root","ORIGIN");
    for(const n of data.nodes) {
      const classification=n.classification;
      const variant=classification==="source_collapse"?"collapse":
                    classification==="dependent"?"dependent":"independent";
      const title="OBSERVATION "+(n.id+1)+" / "+(classification==="source_collapse"?
                   "SOURCE COLLAPSE":classification==="dependent"?"DEPENDENT":"SELF-REPORTED");
      box(n.id,title,n.observation,variant,classification==="source_collapse"?"!":"");
    }
  }
  return {render};
})();