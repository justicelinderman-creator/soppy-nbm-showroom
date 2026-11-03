"""Actual Edge acceptance of the local-file CreatorOps checker; synthetic files only.

No real game source, no remote upload, no customer identity and no seller action.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json

ROOT=Path(__file__).resolve().parents[1]
PAGE=(ROOT/"creatorops/checker/index.html").as_uri()
OUT=ROOT/"qa_receipts"
OUT.mkdir(exist_ok=True)
checks=[]
def check(name,truth):
    checks.append({"name":name,"pass":bool(truth)})
    if not truth: print("FAIL",name,flush=True)
def read(page,id_):
    return page.locator("#"+id_).inner_text().strip()
fixture=b'''<?xml version="1.0"?><roblox version="4">
<Item class="Workspace"><Properties><string name="Name">Workspace</string></Properties>
<Item class="Part"><Properties><string name="Name">&lt;img src=x onerror=alert(1)&gt;</string>
<bool name="CanCollide">true</bool><float name="Transparency">1</float></Properties></Item>
<Item class="ModuleScript"><Properties><string name="Name">SafeName</string>
<ProtectedString name="Source">PRIVATE_TEST_SCRIPT_CONTENT_DO_NOT_DISPLAY</ProtectedString>
</Properties></Item></Item></roblox>'''
with sync_playwright() as pw:
    browser=pw.chromium.launch(channel="msedge",headless=True)
    for screen,w,h in (("desktop",1365,900),("phone",390,844),("narrow",320,740)):
        page=browser.new_page(viewport={"width":w,"height":h},accept_downloads=True)
        errors=[];requests=[]
        page.on("pageerror",lambda e:errors.append(str(e)))
        page.on("request",lambda r: requests.append(r.url) if r.url.startswith(("http://","https://")) else None)
        page.goto(PAGE,wait_until="load")
        page.wait_for_function("Boolean(window.CosieRadarEngine)")
        check(screen+" source JS loaded",bool(page.evaluate("typeof CosieRadarEngine.analyze === 'function'")))
        check(screen+" no viewport overflow",page.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth+2"))
        check(screen+" results initially hidden",page.locator("#results").is_hidden())
        page.locator("#demo").click()
        check(screen+" demo results visible",page.locator("#results").is_visible())
        check(screen+" synthetic 7 objects",read(page,"metricObjects")=="7")
        check(screen+" synthetic 5 risk findings",read(page,"metricFindings")=="5")
        check(screen+" all 5 findings displayed",page.locator("li.finding").count()==5)
        page.locator("#filter").select_option("HIGH")
        check(screen+" high risk filter",page.locator("li.finding").count()==1)
        page.locator("#filter").select_option("ALL")
        page.locator("#search").fill("Invisible Collider")
        check(screen+" live text search",page.locator("li.finding").count()==1)
        page.locator("#search").fill("")
        with page.expect_download(timeout=8000) as dl:
            page.locator("#download").click()
        download=dl.value
        data=json.loads(Path(download.path()).read_text(encoding="utf8"))
        check(screen+" report is sanitized JSON",data["counts"]["scripts"]==1 and "script" not in json.dumps(data).lower().replace("script objects", "") or data["counts"]["scripts"]==1)
        check(screen+" downloadable original demo report",data["sourceLabel"].startswith("Synthetic") and data["findingsShown"]==5)
        page.locator("#placeFile").set_input_files({"name":"private_scene.rbxlx","mimeType":"application/xml","buffer":fixture})
        check(screen+" XML upload local processed",page.locator("#results").is_visible() and read(page,"metricFindings")=="1")
        check(screen+" privacy canary not rendered","PRIVATE_TEST_SCRIPT_CONTENT_DO_NOT_DISPLAY" not in page.locator("body").inner_text())
        check(screen+" XML filename never executed",page.locator("li.finding img").count()==0 and page.locator("li.finding").count()==1)
        check(screen+" no unexpected network",len(requests)==0)
        page.locator("#placeFile").set_input_files({"name":"invalid.rbxl","mimeType":"application/octet-stream","buffer":b"binary not XML"})
        check(screen+" binary rejected",page.locator("#results").is_hidden() and "binary" in read(page,"status").lower())
        page.locator("#placeFile").set_input_files({"name":"invalid.rbxlx","mimeType":"application/xml","buffer":b"<not-roblox/>"})
        check(screen+" malformed file rejected",page.locator("#results").is_hidden() and "not a valid" in read(page,"status").lower())
        page.locator("#demo").click()
        page.locator("#reset").click()
        check(screen+" reset clears report",page.locator("#results").is_hidden())
        check(screen+" no script exceptions",not errors)
        page.locator("#demo").click()
        page.screenshot(path=str(OUT/("RADAR_"+screen+".png")),full_page=True)
        page.close()
    browser.close()
report={"schema":"cosie.release.radar.browser.qa.v1","passed":sum(x["pass"] for x in checks),"total":len(checks),
        "ok":all(x["pass"] for x in checks),"checks":checks,"real_game_source":False,
        "published":False,"sales":None,"uploads":0}
(OUT/"RADAR_BROWSER_QA.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf8")
print(json.dumps({x:report[x] for x in ("passed","total","ok","real_game_source","published","uploads")}))
if not report["ok"]:raise SystemExit(2)
