"""Authorized low-volume Render Gemini check using only a fictional message.

At most one provider inference request after detecting Gemini; no secrets logged.
"""
import json
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError

BASE="https://forgehacks.onrender.com"
MESSAGE="Hello, I am a recruiter for fictional Harbor Systems. We are hiring a Software Engineering intern in July. Please reply if interested."

def fetch(path, body=None):
    payload=None if body is None else json.dumps(body).encode()
    request=Request(BASE+path, data=payload,
                    headers={"Content-Type":"application/json"},
                    method="POST" if payload is not None else "GET")
    try:
        with urlopen(request,timeout=60) as resp:
            return resp.status,json.load(resp)
    except HTTPError as err:
        return err.code,{"error_category":"http_"+str(err.code)}

def main():
    print("GEMINI_LIVE_RENDER_VALIDATION",flush=True)
    for attempt in range(10):
        status,health=fetch("/health")
        print("health",status,health,flush=True)
        if status==200 and health.get("ai_provider")=="gemini":break
        time.sleep(12)
    else:raise AssertionError("Render not yet on Gemini-configured release")
    assert health.get("ai_configured") is True
    # Guarantee that passive local inspection will never expose the message to Gemini.
    status,plain=fetch("/api/analyze",{"message":MESSAGE})
    assert status==200 and plain.get("external_ai_requested") is False
    assert plain.get("mode")=="rules_fallback"
    print("LOCAL_ONLY_PRIVACY_PASS",flush=True)
    # Exactly one consented synthetic request; app may return safe fallback
    # if provider denies quota or key is restricted.
    status,ai=fetch("/api/analyze",{"message":MESSAGE,"groq_consent":True})
    print("AI_HTTP",status,flush=True)
    print("AI_MODE",ai.get("mode"),flush=True)
    print("AI_FAILURE_CATEGORY",ai.get("ai_failure_reason"),flush=True)
    print("CLAIMS_RETURNED",len(ai.get("claims",[])),flush=True)
    assert status==200 and ai.get("verified") is False
    assert ai.get("mode")=="ai_extract","Google configured, but inference did not succeed; inspect failure category"
    print("GOOGLE_GEMINI_LIVE_PASS",flush=True)
if __name__=="__main__":main()
