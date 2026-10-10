"""Playwright E2E smoke for OfferProof's public demo paths (synthetic data only)."""
import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts" / "screenshots"
ARTIFACTS.mkdir(parents=True, exist_ok=True)

def unused_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]

def run():
    port = unused_port()
    env = os.environ.copy()
    env.pop("GROQ_API_KEY", None)
    env.update({"PORT": str(port), "HOST": "127.0.0.1"})
    proc = subprocess.Popen([sys.executable, "offerproof.py"], cwd=ROOT, env=env,
                            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            errors = []
            page = browser.new_page(viewport={"width": 1440, "height": 950}, device_scale_factor=1)
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle", timeout=20000)
            assert page.locator("#overview-title").is_visible()
            page.screenshot(path=str(ARTIFACTS / "desktop-overview.png"), full_page=True)
            page.locator(".case").nth(1).click()
            assert page.locator("#view-inspect").is_visible()
            page.locator("#analyze").click()
            page.locator("#result-title").wait_for(timeout=20000)
            assert "unverified" in page.locator("#result-title").inner_text().lower()
            assert "local-only" in page.locator("#mode").inner_text().lower()
            page.screenshot(path=str(ARTIFACTS / "desktop-inspection.png"), full_page=True)
            page.locator("[data-go='evidence']").click()
            page.locator("#evidence-log").get_by_text("jobs.harborsystems.example", exact=False).wait_for(timeout=12000)
            assert "not visited" in page.locator("#evidence-log").inner_text()
            page.locator("#load-evidence-demo").click()
            page.get_by_text("Source collapse detected.", exact=False).wait_for(timeout=10000)
            assert "Source collapse detected" in page.locator("#collapse-notice").inner_text()
            assert page.locator(".evidence-svg path").count() >= 3
            assert page.locator(".evidence-svg text").count() >= 8
            page.screenshot(path=str(ARTIFACTS / "desktop-evidence.png"), full_page=True)
            with page.expect_download() as download_info:
                page.locator("#download-case").click()
            assert download_info.value.suggested_filename == "OfferProof-investigation.txt"
            page.locator(".nav button[data-view='response']").click()
            page.locator("input[value='shared_password']").check()
            page.locator("#respond").click()
            page.locator("#response-steps li").first.wait_for(timeout=10000)
            assert "password" in page.locator("#response-steps").inner_text().lower()
            page.screenshot(path=str(ARTIFACTS / "desktop-response.png"), full_page=True)
            assert not errors, errors
            page.locator(".nav button[data-view='overview']").click()
            page.locator("#run-demo").click()
            page.get_by_text("Source collapse detected.", exact=False).wait_for(timeout=15000)
            assert page.locator(".evidence-svg path").count() >= 4
            page.locator("#compare-case").click()
            assert "Confirm" in page.locator("#compare-message").inner_text()
            page.locator("#consent-review").check()
            page.locator("#compare-case").click()
            page.locator("#compare-mode").wait_for(timeout=15000)
            assert "unavailable" in page.locator("#compare-mode").inner_text().lower()
            page.screenshot(path=str(ARTIFACTS / "desktop-ai-review-fallback.png"), full_page=True)
            page.locator("#observation").fill("<img src=x onerror=alert(7)>")
            page.locator("#record").click()
            page.locator("#evidence-log").get_by_text("<img src=x onerror=alert(7)>", exact=False).wait_for(timeout=12000)
            assert page.locator("#graph img").count() == 0
            assert page.locator(".evidence-svg path").count() >= 4
            mobile = browser.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=1)
            mobile.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle", timeout=20000)
            assert mobile.locator("#overview-title").is_visible()
            overflow = mobile.evaluate("document.documentElement.scrollWidth - window.innerWidth")
            assert overflow <= 2, f"mobile horizontal overflow: {overflow}px"
            mobile.screenshot(path=str(ARTIFACTS / "mobile-overview.png"), full_page=True)
            mobile.locator(".nav button[data-view='inspect']").click()
            assert mobile.locator("#view-inspect").is_visible()
            assert mobile.locator("#message").is_visible()
            mobile.locator(".nav button[data-view='evidence']").click()
            mobile.locator("#load-evidence-demo").click()
            mobile.locator(".evidence-svg path").first.wait_for(timeout=12000)
            overflow = mobile.evaluate("document.documentElement.scrollWidth - window.innerWidth")
            assert overflow <= 2, f"mobile evidence overflow: {overflow}px"
            browser.close()
        print("PASS: desktop overview, analysis, source collapse, recovery, mobile navigation and overflow")
    finally:
        proc.terminate()
        try: proc.communicate(timeout=5)
        except subprocess.TimeoutExpired: proc.kill()

if __name__ == "__main__":
    run()
