#!/usr/bin/env python3
"""Manual IndexNow notification for genuinely new or edited showroom URLs.

No automatic submits, indexing guarantees, user tracking or account changes.
Only submits known project-relative routes to the official IndexNow endpoint
after confirming the public key is served at its expected full URL.
"""
from __future__ import annotations
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import argparse
import json

KEY = "CosieNBM6c6beeb8c0098e16c894de41005b9146"
HOST = "justicelinderman-creator.github.io"
BASE = "https://justicelinderman-creator.github.io/soppy-nbm-showroom/"
KEY_LOCATION = BASE + KEY + ".txt"
API = "https://api.indexnow.org/indexnow"
ROUTES = (
    "",
    "studio/",
    "services/",
    "services/n8n/",
    "roblox-qa/",
    "guides/roblox-release-checklist/",
    "guides/n8n-webhook-reliability/",
)

def payload() -> dict:
    urls = [BASE + route for route in ROUTES]
    assert len(urls) == len(set(urls))
    assert all(urlparse(url).hostname == HOST and url.startswith(BASE) for url in urls)
    return {"host": HOST, "key": KEY, "keyLocation": KEY_LOCATION, "urlList": urls}

def main() -> None:
    parser = argparse.ArgumentParser(description="Submit only recently revised Cosie-owned URLs to IndexNow")
    parser.add_argument("--submit", action="store_true", help="Opt-in: POST one batch to official IndexNow")
    args = parser.parse_args()
    result = payload()
    if not args.submit:
        print(json.dumps({"status": "DRY_RUN", "key_url": KEY_LOCATION,
            "url_count": len(result["urlList"]), "urls": result["urlList"],
            "submitted": False}, indent=2))
        return
    with urlopen(Request(KEY_LOCATION, headers={"User-Agent": "Cosie-IndexNow/1.0"}), timeout=20) as response:
        public_key = response.read(128).decode("utf-8").strip()
    if public_key != KEY:
        raise RuntimeError("The public key is missing or does not match; refusing to submit.")
    request = Request(API, method="POST", headers={"Content-Type":"application/json; charset=utf-8",
        "User-Agent":"Cosie-IndexNow/1.0"}, data=json.dumps(result).encode("utf-8"))
    try:
        with urlopen(request, timeout=25) as response:
            status = response.status
            explanation = response.read(1000).decode("utf-8", errors="replace")
    except HTTPError as error:
        status = error.code
        explanation = error.read(1000).decode("utf-8", errors="replace")
    print(json.dumps({"status":"REQUEST_RECEIVED" if status in (200,202) else "REJECTED",
         "http_status":status,"engine_response":explanation[:180],
         "submitted_urls":len(result["urlList"]), "indexed_not_verified":True}, indent=2))
    if status not in (200,202):
        raise SystemExit(2)

if __name__ == "__main__":
    main()
