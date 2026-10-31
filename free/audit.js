/* Browser-only quote-flow self audit. No storage, tracking, or network transmission. */
(() => {
  "use strict";
  const checks = Array.from(document.querySelectorAll('main input[type="checkbox"]'));
  const score = document.getElementById("audit-score");
  const bar = document.getElementById("audit-fill");
  const summary = document.getElementById("audit-priority");
  const copyButton = document.getElementById("copy-audit");
  const resetButton = document.getElementById("reset-audit");
  const notice = document.getElementById("copy-status");
  const manual = document.getElementById("audit-manual");
  const groups = ["Clarity", "Mobile", "Trust and delivery"];
  if (checks.length !== 12 || !score || !bar || !summary || !copyButton || !resetButton || !notice || !manual) return;

  function missed() {
    return checks
      .map((check, index) => ({ index, label: check.closest("label")?.textContent.trim() || "" }))
      .filter((item) => !checks[item.index].checked);
  }
  function prioritized(items) {
    const order = [10, 6, 2, 5, 11, 7, 0, 1, 3, 4, 8, 9];
    return items.slice().sort((a, b) => order.indexOf(a.index) - order.indexOf(b.index));
  }
  function update() {
    const passed = checks.filter((check) => check.checked).length;
    score.textContent = passed + " / 12 checks passed";
    bar.style.width = Math.round(passed * 100 / 12) + "%";
    const gaps = prioritized(missed());
    summary.textContent = gaps.length
      ? "Start here: " + gaps.slice(0, 3).map((item) => item.label).join(" ") + " Check those items before paying for more traffic."
      : "All 12 self-check items are marked complete. Test your site with a real person and recheck after changes; this is not a conversion guarantee.";
    notice.textContent = "";
    manual.hidden = true;
  }
  function report() {
    const passed = checks.filter((check) => check.checked).length;
    const gaps = prioritized(missed());
    const lines = [
      "NBM DELIVERY STUDIO — 12-POINT QUOTE-FLOW SELF-AUDIT",
      "Checks passed: " + passed + "/12",
      "Self-assessment only; no promise of sales or conversion improvements.",
      "",
      "Highest-priority next steps:"
    ];
    if (gaps.length) gaps.forEach((item, i) => lines.push((i + 1) + ". [" + groups[Math.floor(item.index / 4)] + "] " + item.label));
    else lines.push("All boxes are checked. Retest contact delivery and usability with real visitors.");
    lines.push("", "Generated locally in the browser. No details transmitted to NBM.");
    return lines.join("\n");
  }

  checks.forEach((check) => check.addEventListener("change", update));
  resetButton.addEventListener("click", () => {
    checks.forEach((check) => { check.checked = false; });
    update();
  });
  copyButton.addEventListener("click", async () => {
    const value = report();
    try {
      if (!navigator.clipboard?.writeText) throw Error("clipboard unsupported");
      await navigator.clipboard.writeText(value);
      notice.textContent = "Audit action plan copied. You can paste it into your own notes.";
      manual.hidden = true;
    } catch (_err) {
      manual.hidden = false;
      manual.value = value;
      manual.focus();
      manual.select();
      notice.textContent = "Automatic copy unavailable. Select and copy the text below.";
    }
  });
  update();
})();
