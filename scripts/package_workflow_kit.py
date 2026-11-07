#!/usr/bin/env python3
"""Package the reviewed public tool and templates into a portable free kit."""
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools/workflow-preflight"
OUTPUT = ROOT / "downloads/cosie-workflow-rescue-kit.zip"
PUBLIC = "https://justicelinderman-creator.github.io/soppy-nbm-showroom/"
FILES = (
    "README.md", "index.html", "styles.css", "app.js", "preflight.js", "samples.js",
    "incident-intake.md", "acceptance-checklist.md", "rollback-plan.md", "handoff-template.md",
    "fixtures/valid.json", "fixtures/dangling.json", "fixtures/malformed.json",
)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(OUTPUT, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    for relative in FILES:
        data = (SOURCE / relative).read_bytes()
        if relative == "index.html":
            html = data.decode("utf-8")
            for target in ("", "services/n8n/#brief", "downloads/cosie-workflow-rescue-kit.zip"):
                html = html.replace('href="../../' + target + '"', 'href="' + PUBLIC + target + '"')
            data = html.encode("utf-8")
        archive.writestr("cosie-workflow-rescue-kit/" + relative, data)

with zipfile.ZipFile(OUTPUT) as archive:
    assert archive.testzip() is None
    assert len(archive.namelist()) == len(FILES)
print(f"Packaged {len(FILES)} files, {OUTPUT.stat().st_size} bytes: {OUTPUT.name}")
