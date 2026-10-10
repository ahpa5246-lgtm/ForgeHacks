"""Read-only/lightweight E2E audit of the owner's public Render demonstration.
Only synthetic messages are submitted. At most one explicit Groq analyze request
and one Groq compare request. No load testing, crawling, or real user data.
"""
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "https://forgehacks.onrender.com"
SHOTS = Path("artifacts/live-render")
SHOTS.mkdir(parents=True, exist_ok=True)
MSG = ("Hello, I am a recruiter for Harbor Systems. We invite you to interview "
       "for a Software Engineering internship starting July 1. See "
       "https://jobs.harborsystems.example/roles/421 for details, "
       "then reply if interested.")
NOTES = [
  {"kind":"other","source":"message","observation":"The sender linked a careers page."},
  {"kind":"company_careers","source":"independent","derived_from":[0],
   "observation":"I reached the role listing through the sender link."},
  {"kind":"company_contact","source":"independent",
   "observation":"An independent employer channel described a Data Analyst internship starting August."},
  {"kind":"other","source":"independent","derived_from":[1,2],
   "observation":"A synthesis combines the recruiter link with a separate contact."}
]

def req(path="/",payload=None,timeout=100):
    data=None if payload is None else json.dumps(payload).encode("utf-8")
    r=urllib.request.Request(
        BASE+path,data=data,
        headers={"User-Agent":"OfferProof-authorized-demo-audit/1.0",
                 "Content-Type":"application/json" if data is not None else "text/plain"},
        method="POST" if data is not None else "GET"
    )
    t=time.monotonic()
    try:
        with urllib.request.urlopen(r,timeout=timeout) as response:
            status=response.status
            headers=dict(response.headers.items())
            body=response.read(500_000)
    except urllib.error.HTTPError as exc:
        status=exc.code
        headers=dict(exc.headers.items())
        body=exc.read(500_000)
    elapsed=time.monotonic()-t
    print("HTTP",path,status,round(elapsed,2),"s","bytes",len(body),flush=True)
    return status,headers,body

def decoded(body):
    return json.loads(body.decode("utf-8"))

def require(condition,message):
    if not condition:
        raise AssertionError(message)

def main():
    print("PUBLIC_RENDER_AUDIT",BASE,flush=True)
    print("All payloads below are fictional; no keys, real messages or personal data used.")
    home=None
    for attempt in range(3):
        try:
            home=req("/",timeout=120)
            if home[0]==200:break
        except Exception as exc:
            print("Wake attempt",attempt+1,type(exc).__name__,str(exc)[:90],flush=True)
        time.sleep(8)
    require(home is not None and home[0]==200,"Homepage unreachable after Render cold-start attempts")
    html=home[2].decode("utf-8")
    require("id=\"run-demo\"" in html and "id=\"ai-consent\"" in html,
            "Production HTML is outdated (missing latest demo/privacy controls)")
    require("/source_graph.js" in html and "id=\"compare-case\"" in html,
            "Production HTML lacks SVG evidence graph or comparison view")
    print("FRONTEND_DEPLOYMENT latest v5 markers verified",flush=True)
    _,headers,_=home
    assert any("script-src 'self'" in str(v) for k,v in headers.items()
               if k.lower()=="content-security-policy"),"No expected CSP header"

    status,_,raw=req("/health",timeout=65)
    require(status==200,"Health endpoint failed")
    health=decoded(raw)
    print("HEALTH_CONFIG",json.dumps(health),flush=True)
    require(health.get("ok") is True,"Health did not report ok")

    for path,token in (
        ("/dashboard.js","message_source_seeds"),
        ("/source_graph.js","OfferProofGraph"),
        ("/dashboard.css",".evidence-svg")
    ):
        status,headers,body=req(path,timeout=65)
        require(status==200 and token in body.decode("utf-8"),
                path+" is stale or missing")
        if path=="/dashboard.js":
            require("ai_failure_reason" in body.decode("utf-8"),
                    "Render has not deployed the current Groq diagnostics release yet")
    status,_,_=req("/.env",timeout=65)
    require(status==404,"Sensitive file route was not blocked")

    status,_,raw=req("/api/analyze",{"message":MSG},timeout=70)
    require(status==200,"Local analysis failed")
    local=decoded(raw)
    require(local.get("mode")=="rules_fallback" and
            local.get("external_ai_requested") is False,
            "Local-by-default privacy requirement is broken")
    require(any("jobs.harborsystems.example" in x.get("observation","")
                for x in local.get("message_source_seeds",[])),
            "Backend did not extract untrusted sender-host seed")
    require(local.get("verified") is False,"Safety boundary was broken")
    print("LOCAL_ONLY",local["mode"],"source_leads",len(local["message_source_seeds"]),flush=True)

    status,_,raw=req("/api/assess",{"evidence":NOTES},timeout=65)
    require(status==200,"Evidence API failed")
    graph=decoded(raw)
    require(graph.get("source_collapses")==[1,3],
            "Provenance traversal does not propagate two-level dependencies")
    require(len(graph.get("edges",[]))>=4 and
            graph.get("sender_authenticated") is False,
            "Directed graph structure or sender trust boundary failed")
    print("DAG","nodes",len(graph["nodes"]),"edges",len(graph["edges"]),
          "collapses",graph["source_collapses"],flush=True)

    status,_,raw=req("/api/compare",{"message":MSG,"evidence":NOTES},timeout=65)
    require(status==400,"Cross-evidence endpoint allows Groq without explicit consent")
    print("CONSENT_ENFORCEMENT",status,flush=True)

    status,_,raw=req("/api/respond",{"events":["shared_password"]},timeout=65)
    require(status==200 and "password" in json.dumps(decoded(raw)).lower(),
            "Recovery API failed")

    # At most one direct live inference attempt. The response is not a scam verdict.
    if health.get("ai_configured"):
        status,_,raw=req("/api/analyze",
                          {"message":MSG,"groq_consent":True},timeout=80)
        require(status==200,"Consented AI analyze request failed at HTTP level")
        result=decoded(raw)
        print("LIVE_GROQ_ANALYSIS",result.get("mode"),"failure_reason",result.get("ai_failure_reason"),
              "claim_count",len(result.get("claims",[])),
              "attention_count",len(result.get("ai_attention",[])),
              "verified",result.get("verified"),flush=True)
        require(result.get("verified") is False,"AI authenticity safety boundary broken")
    else:
        print("LIVE_GROQ_ANALYSIS_SKIPPED: environment key not configured",flush=True)

    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        page=browser.new_page(viewport={"width":1365,"height":900})
        errs=[]
        page.on("pageerror",lambda e: errs.append(str(e)))
        response=page.goto(BASE+"/",wait_until="networkidle",timeout=120_000)
        require(response and response.status==200,"Browser cannot open Render homepage")
        page.locator("#overview-title").wait_for(timeout=15000)
        page.screenshot(path=str(SHOTS/"01-home-desktop.png"),full_page=True)
        page.locator(".case[data-sample='B']").click()
        page.locator("#analyze").click()
        page.locator("#result-title").wait_for(timeout=35000)
        require("local-only" in page.locator("#mode").inner_text(),
                "The visible privacy/fallback mode is incorrect")
        page.screenshot(path=str(SHOTS/"02-inspection.png"),full_page=True)
        page.locator("[data-go='evidence']").click()
        page.locator("#evidence-log").get_by_text(
            "jobs.harborsystems.example",exact=False).wait_for(timeout=35000)
        page.locator("#load-evidence-demo").click()
        page.get_by_text("Source collapse detected.",exact=False).wait_for(timeout=35000)
        require(page.locator(".evidence-svg > g path").count()>=4,
                "Rendered source graph lacks real dependency edges")
        page.screenshot(path=str(SHOTS/"03-evidence.png"),full_page=True)
        with page.expect_download(timeout=20000) as download:
            page.locator("#download-case").click()
        require(download.value.suggested_filename.endswith(".txt"),
                "Report cannot be downloaded")
        print("CHROMIUM_DESKTOP dashboard, claims, source graph, export PASS",flush=True)

        # One live Groq comparison request through the actual UI, if configured.
        if health.get("ai_configured"):
            page.locator("#consent-review").check()
            page.locator("#compare-case").click()
            page.locator("#compare-mode").wait_for(timeout=42000)
            mode=page.locator("#compare-mode").inner_text()
            print("LIVE_GROQ_COMPARISON_UI",mode[:120],flush=True)
            page.screenshot(path=str(SHOTS/"04-live-cross-evidence.png"),full_page=True)
        page.locator(".nav button[data-view='response']").click()
        page.locator("input[value='shared_password']").check()
        page.locator("#respond").click()
        page.locator("#response-steps li").first.wait_for(timeout=20000)
        print("CHROMIUM_RECOVERY PASS",flush=True)
        require(not errs,"Browser JS errors: "+repr(errs),)
        mobile=browser.new_page(viewport={"width":390,"height":844},
                                device_scale_factor=1)
        mobile.goto(BASE+"/",wait_until="networkidle",timeout=120_000)
        mobile.locator("#overview-title").wait_for(timeout=15000)
        overflow=mobile.evaluate(
            "document.documentElement.scrollWidth - window.innerWidth")
        require(overflow<=2,f"Mobile homepage horizontal overflow: {overflow}px")
        mobile.screenshot(path=str(SHOTS/"05-mobile-overview.png"),full_page=True)
        mobile.locator(".nav button[data-view='evidence']").click()
        mobile.locator("#load-evidence-demo").click()
        mobile.locator(".evidence-svg > g path").first.wait_for(state="attached",timeout=20000)
        overflow=mobile.evaluate(
            "document.documentElement.scrollWidth - window.innerWidth")
        require(overflow<=2,f"Mobile evidence page horizontal overflow: {overflow}px")
        mobile.screenshot(path=str(SHOTS/"06-mobile-evidence.png"),full_page=True)
        browser.close()
        print("CHROMIUM_MOBILE 390px overflow, navigation and graph PASS",flush=True)
    print("LIVE_RENDER_AUDIT_COMPLETE",flush=True)

if __name__=="__main__":
    main()
