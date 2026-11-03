"""Real Microsoft Edge rendering checks for a pre-release creator plugin info page.

Does not click mailto, submit forms, download plugins, or access seller accounts.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"qa_receipts"
OUT.mkdir(exist_ok=True)
results=[]
def ok(label,result):
    results.append((label,bool(result)))
    if not result:print("FAIL",label,flush=True)

with sync_playwright() as pw:
    browser=pw.chromium.launch(channel="msedge",headless=True)
    for label,w,h,mobile in [
        ("desktop",1365,900,False),("phone",390,844,True),("narrow_phone",320,740,True)
    ]:
        page=browser.new_page(viewport={"width":w,"height":h},
            is_mobile=mobile,has_touch=mobile,device_scale_factor=1)
        errors=[]
        page.on("pageerror",lambda x:errors.append(str(x)))
        page.goto((ROOT/"creatorops/index.html").as_uri(),wait_until="load")
        ok(label+" accurate hero",page.locator("h1").is_visible() and "AUDIT." in page.locator("h1").inner_text())
        ok(label+" pre-release label",page.get_by_text("Private development candidate",exact=False).count()>0)
        ok(label+" two feature cards",page.locator("article.card").count()==2)
        ok(label+" beta interest mailto available",page.locator('a[href^="mailto:justice.linderman@gmail.com?subject=Cosie%20Studio"]').count()==3)
        ok(label+" no on-site data collection",page.locator("form,input,textarea,script,iframe").count()==0)
        ok(label+" no horizontal overflow",page.evaluate("document.documentElement.scrollWidth<=document.documentElement.clientWidth+2"))
        ok(label+" canonical/indexable",page.locator('meta[name="robots"]').get_attribute("content")=="index,follow" and page.locator('link[rel="canonical"]').count()==1)
        ok(label+" no page errors",len(errors)==0)
        ok(label+" public privacy/nav available",page.locator('a[href="../privacy.html"]').count()>=1 and page.locator('a[href="../studio/"]').count()>=1)
        ok(label+" body stylesheet loaded",page.evaluate("getComputedStyle(document.body).backgroundColor")!="rgba(0, 0, 0, 0)")
        page.screenshot(path=str(OUT/("COSIE_COMPANION_BETA_"+label+".png")),full_page=True)
        page.close()
    browser.close()

receipt={"suite":"cosie.companion.public.beta.browser.v1","checks":[{"name":a,"pass":b} for a,b in results],
"total":len(results),"passed":sum(x[1] for x in results),"ok":all(x[1] for x in results),
"external_actions":{"posts":0,"emails":0,"downloads":0,"purchases":0},
"native_qa_verified":False,"paid_customers_verified":None}
(OUT/"CREATOROPS_BETA_BROWSER_QA.json").write_text(json.dumps(receipt,indent=2))
print(json.dumps({v:receipt[v] for v in ("passed","total","ok","external_actions")}))
if not receipt["ok"]:raise SystemExit(2)
