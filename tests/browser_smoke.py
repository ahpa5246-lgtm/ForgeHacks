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
            assert "fallback" in page.locator("#mode").inner_text().lower()
            page.screenshot(path=str(ARTIFACTS / "desktop-inspection.png"), full_page=True)
            page.locator("[data-go='evidence']").click()
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
            mobile = browser.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=1)
            mobile.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle", timeout=20000)
            assert mobile.locator("#overview-title").is_visible()
            overflow = mobile.evaluate("document.documentElement.scrollWidth - window.innerWidth")
            assert overflow <= 2, f"mobile horizontal overflow: {overflow}px"
            mobile.screenshot(path=str(ARTIFACTS / "mobile-overview.png"), full_page=True)
            mobile.locator(".nav button[data-view='inspect']").click()
            assert mobile.locator("#view-inspect").is_visible()
            assert mobile.locator("#message").is_visible()
            browser.close()
        print("PASS: desktop overview, analysis, source collapse, recovery, mobile navigation and overflow")
    finally:
        proc.terminate()
        try: proc.communicate(timeout=5)
        except subprocess.TimeoutExpired: proc.kill()

if __name__ == "__main__":
    run()
