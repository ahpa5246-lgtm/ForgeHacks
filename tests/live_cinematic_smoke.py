"""Public, low-volume acceptance test of the production cinematic release.

Read-only UI smoke apart from two synthetic local-rule API calls and one synthetic
source-map run. Does not enable Groq, access external sites, load test or send PII.
"""
from pathlib import Path
import time
from playwright.sync_api import sync_playwright

URL = "https://forgehacks.onrender.com"
OUT = Path("artifacts/cinematic-render")
OUT.mkdir(parents=True, exist_ok=True)

def check(condition, message):
    if not condition:
        raise AssertionError(message)

def main():
    print("PRODUCTION_CINEMATIC_AUDIT",URL,flush=True)
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        desktop=browser.new_page(viewport={"width":1440,"height":900},
                                 device_scale_factor=1)
        errors=[]
        desktop.on("pageerror",lambda e:errors.append(str(e)))
        response=None
        for attempt in range(7):
            try:
                response=desktop.goto(URL+"/",wait_until="networkidle",timeout=90000)
                if response and response.status==200 and desktop.locator(".chapter").count()==3:
                    break
            except Exception as exc:
                print("RETRY",attempt+1,type(exc).__name__,flush=True)
            desktop.wait_for_timeout(12000)
        check(response and response.status==200,"Site did not serve 200")
        check(desktop.locator("#overview-title").is_visible(),"Overview title missing")
        check(desktop.locator(".chapter").count()==3,"New story content is not deployed")
        check(desktop.locator("#story-demo").is_visible(),"Story demo trigger missing")
        check(desktop.locator(".hero-art .scene-card").count()==3,"Illustrated evidence cards missing")
        check(desktop.locator("#overview-demo").count()==1,"Original sample action missing")
        check(desktop.locator("#run-demo").is_visible(),"Real demo action missing")
        check(desktop.evaluate("document.documentElement.scrollWidth <= innerWidth + 2"),
              "Desktop horizontal overflow")
        check(desktop.locator(".chapter").first.evaluate(
                "el => parseFloat(getComputedStyle(el).opacity)")>=0.9,
              "Cinematic story is hidden before user scrolling")
        check(not errors,"Page JavaScript errors: "+repr(errors))
        print("PRODUCTION_DESKTOP_UI PASS",flush=True)
        desktop.screenshot(path=str(OUT/"desktop-story.png"),full_page=True)

        desktop.locator(".chapter").nth(2).scroll_into_view_if_needed()
        desktop.wait_for_timeout(1000)
        check(desktop.locator(".chapter").nth(2).is_visible(),
              "Third story chapter cannot be reached")
        desktop.screenshot(path=str(OUT/"desktop-third-act.png"),full_page=False)

        # One-click demo uses the actual server logic and synthetic inputs.
        desktop.locator("#story-demo").click()
        desktop.locator("#view-evidence:not([hidden])").wait_for(timeout=24000)
        desktop.get_by_text("Source collapse detected.",exact=False).wait_for(timeout=12000)
        check(desktop.locator(".evidence-svg .graph-edges > path").count()>=4,
              "DAG edges were not created")
        check(desktop.locator(".evidence-svg .graph-stage-node").count()>=5,
              "Graph nodes missing")
        check(not errors,"JS errors during demo: "+repr(errors))
        desktop.wait_for_timeout(950)
        desktop.screenshot(path=str(OUT/"desktop-evidence-reveal.png"),full_page=True)
        print("PRODUCTION_ONE_CLICK_DEMO PASS",flush=True)

        mobile=browser.new_page(viewport={"width":390,"height":844},device_scale_factor=1)
        mobile_errors=[]
        mobile.on("pageerror",lambda e:mobile_errors.append(str(e)))
        mobile.goto(URL+"/",wait_until="networkidle",timeout=85000)
        check(mobile.locator(".chapter").count()==3,"Mobile chapters missing")
        check(mobile.locator("#overview-title").is_visible(),"Mobile hero missing")
        check(mobile.evaluate("document.documentElement.scrollWidth <= innerWidth + 2"),
              "Mobile horizontal overflow")
        mobile.screenshot(path=str(OUT/"mobile-story.png"),full_page=True)
        mobile.locator("#story-demo").click()
        mobile.locator("#view-evidence:not([hidden])").wait_for(timeout=20000)
        mobile.get_by_text("Source collapse detected.",exact=False).wait_for(timeout=10000)
        check(mobile.evaluate("document.documentElement.scrollWidth <= innerWidth + 2"),
              "Mobile graph breaks viewport")
        mobile.wait_for_timeout(950)
        mobile.screenshot(path=str(OUT/"mobile-evidence.png"),full_page=True)
        check(not mobile_errors,"Mobile JS errors: "+repr(mobile_errors))
        print("PRODUCTION_MOBILE PASS",flush=True)

        no_motion=browser.new_page(viewport={"width":960,"height":780},reduced_motion="reduce")
        no_motion.goto(URL+"/",wait_until="networkidle",timeout=85000)
        check(not no_motion.evaluate("document.documentElement.classList.contains('js-motion')"),
              "Motion preference ignored")
        print("PRODUCTION_REDUCED_MOTION PASS",flush=True)
        browser.close()
    print("PRODUCTION_CINEMATIC_AUDIT_COMPLETE",flush=True)

if __name__=="__main__":
    main()
