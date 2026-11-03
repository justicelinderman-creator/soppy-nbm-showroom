"""Real Edge acceptance for owner's original 3D portfolio + NBM service discoverability.

Runs against isolated local staging, not the live site. Never uploads, submits,
sends, purchases or writes client data. Requires Playwright + Microsoft Edge.
"""
from pathlib import Path
import json,hashlib
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"qa_receipts";OUT.mkdir(exist_ok=True)
results=[]
def ck(name,passed):
    results.append((name,bool(passed)))
    if not passed:print("FAIL:",name,flush=True)
with sync_playwright() as pw:
    browser=pw.chromium.launch(channel="msedge",headless=True)
    for name,w,h,mobile in [("desktop",1365,900,False),("phone",390,844,True),("smallphone",320,740,True)]:
        page=browser.new_page(viewport={"width":w,"height":h},is_mobile=mobile,has_touch=mobile,device_scale_factor=1)
        errors=[];page.on("pageerror",lambda e: errors.append(str(e)))
        page.goto((ROOT/"portfolio/facility-console/index.html").as_uri(),wait_until="load")
        ck(name+" original portfolio hero",page.locator("h1").inner_text().replace("\n"," ").startswith("Facility"))
        for img in page.locator("img").all():
            img.scroll_into_view_if_needed()
        page.wait_for_function("Array.from(document.images).every(x=>x.complete && x.naturalWidth>0)")
        ck(name+" image load",page.locator("img").count()==3 and page.locator("img").evaluate_all("(xs)=>xs.every(x=>x.complete && x.naturalWidth>0)"))
        ck(name+" two email inquiry links",page.locator('a[href^="mailto:justice.linderman@gmail.com"]').count()==2)
        ck(name+" no horizontal overflow",page.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth+2"))
        ck(name+" no active forms or scripts",page.locator("form,input,iframe,script").count()==0)
        ck(name+" no page error",not errors)
        ck(name+" visible CTA",page.locator('a.btn[href^="mailto:justice.linderman@gmail.com"]').is_visible())
        ck(name+" indexable canonical",page.locator('meta[name="robots"]').get_attribute("content")=="index,follow" and page.locator('link[rel="canonical"]').count()==1)
        page.screenshot(path=str(OUT/("COSIE_PORTFOLIO_"+name+".png")),full_page=True)
        page.goto((ROOT/"studio/index.html").as_uri(),wait_until="load")
        ck(name+" NBM studio indexed",page.locator('meta[name="robots"]').get_attribute("content")=="index,follow")
        ck(name+" studio to portfolio nav",page.locator('a[href="../portfolio/facility-console/"]').count()>=1)
        ck(name+" NBM email still visible",page.locator('a[href^="mailto:justice.linderman@gmail.com"]').count()>=2)
        page.close()
    browser.close()
receipt={"schema":"cosie.first-buyer.public.browser.qa.r01","tests":[{"name":a,"ok":b} for a,b in results],
"passed":sum(b for _,b in results),"total":len(results),"ok":all(b for _,b in results),
"external_actions":0,"actual_customer_orders":None,"published_site_verified":False}
(OUT/"COSIE_FIRST_BUYER_BROWSER_QA.json").write_text(json.dumps(receipt,indent=2),encoding="utf8")
print(json.dumps({x:receipt[x] for x in ("passed","total","ok","external_actions")},indent=2))
if not receipt["ok"]:raise SystemExit(2)
