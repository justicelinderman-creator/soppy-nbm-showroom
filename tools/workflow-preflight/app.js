(function () {
  'use strict';
  const api = window.WorkflowPreflight;
  const $ = id => document.getElementById(id);
  let current = null;
  let generation = 0;
  function element(tag, text, className) {
    const item = document.createElement(tag);
    if (text !== undefined) item.textContent = text;
    if (className) item.className = className;
    return item;
  }
  function inventory() {
    const rows = $('node-rows');
    rows.replaceChildren();
    if (!current) return;
    for (const node of current.nodes) {
      const row = element('tr');
      const identity = element('td', node.alias);
      if ($('reveal-names').checked && node.name) identity.append(element('small', node.name));
      const notes = [];
      if (node.disabled) notes.push('Disabled');
      if (node.credentials) notes.push('Credential reference');
      if (node.isHttp) notes.push('Retry: ' + node.retry);
      notes.push(node.incoming + ' in / ' + node.outgoing + ' out');
      row.append(identity, element('td', node.typeLabel), element('td', notes.join(' · ')));
      rows.append(row);
    }
  }
  function render(report, message) {
    current = report;
    $('empty').hidden = true;
    $('results').hidden = false;
    $('result-status').textContent = api.status(report);
    $('result-summary').textContent = report.counts.error + ' structural issue(s) · ' + report.counts.review + ' setting review(s) · ' + report.counts.info + ' information item(s). No live execution was performed.';
    $('metric-nodes').textContent = report.totals.nodes;
    $('metric-connections').textContent = report.totals.connectionEntries;
    $('metric-types').textContent = report.totals.distinctTypes;
    $('metric-findings').textContent = report.counts.error + report.counts.review;
    $('inventory-count').textContent = '(' + report.nodes.length + ')';
    const findings = $('findings');
    findings.replaceChildren();
    for (const finding of report.findings) {
      const card = element('article', undefined, 'finding');
      const top = element('div', undefined, 'finding-top');
      top.append(element('span', finding.severity === 'error' ? 'Issue' : finding.severity, 'badge ' + finding.severity), element('h4', finding.title));
      card.append(top, element('p', finding.detail));
      if (finding.nodes.length) card.append(element('p', finding.nodes.join(' · '), 'aliases'));
      findings.append(card);
    }
    if (!report.findings.length) findings.append(element('p', 'No issues were detected by these structural checks. Live behavior still needs testing.', 'clear-finding'));
    $('reveal-names').checked = false;
    inventory();
    $('brief-preview').textContent = api.buildBrief(report);
    $('notice').textContent = message + ' ' + api.status(report) + '.';
  }
  function clear() {
    generation++;
    current = null;
    $('workflow-file').value = '';
    $('workflow-text').value = '';
    $('reveal-names').checked = false;
    $('node-rows').replaceChildren();
    $('findings').replaceChildren();
    $('brief-preview').textContent = '';
    $('results').hidden = true;
    $('empty').hidden = false;
    $('notice').textContent = 'Loaded data cleared from this tool. Any files you downloaded remain on your device.';
  }
  $('workflow-file').addEventListener('change', async event => {
    const file = event.target.files[0];
    if (!file) return;
    const token = ++generation;
    $('workflow-text').value = '';
    if (file.size > api.LIMITS.bytes) {
      clear();
      $('notice').textContent = 'This file exceeds 5 MiB. Choose a smaller, single workflow export.';
      return;
    }
    $('notice').textContent = 'Reading the selected file locally…';
    try {
      const text = await file.text();
      if (token !== generation) return;
      render(api.analyze(text), 'File reviewed locally.');
    } catch (_) {
      if (token !== generation) return;
      clear();
      $('notice').textContent = 'This file could not be read. Try exporting it again from n8n.';
    }
  });
  $('review-paste').addEventListener('click', () => {
    generation++;
    $('workflow-file').value = '';
    render(api.analyze($('workflow-text').value), 'Pasted JSON reviewed locally.');
  });
  document.querySelectorAll('[data-sample]').forEach(button => button.addEventListener('click', () => {
    generation++;
    $('workflow-file').value = '';
    $('workflow-text').value = '';
    render(api.analyze(window.PreflightSamples[button.dataset.sample]), 'Synthetic sample reviewed; nothing was executed.');
  }));
  $('reveal-names').addEventListener('change', inventory);
  $('clear').addEventListener('click', clear);
  $('download').addEventListener('click', () => {
    if (!current) return;
    const url = URL.createObjectURL(new Blob([api.buildBrief(current)], { type: 'text/markdown;charset=utf-8' }));
    const link = element('a');
    link.href = url;
    link.download = 'workflow-preflight-brief.md';
    document.body.append(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    $('notice').textContent = 'Brief download requested. Review it before sharing; node names stay redacted.';
  });
  $('copy').addEventListener('click', async () => {
    if (!current) return;
    try {
      if (!navigator.clipboard) throw new Error('Clipboard unavailable');
      await navigator.clipboard.writeText(api.buildBrief(current));
      $('notice').textContent = 'Redacted brief copied. Review it before sharing.';
    } catch (_) {
      document.querySelector('.brief-details').open = true;
      const selection = window.getSelection();
      const range = document.createRange();
      range.selectNodeContents($('brief-preview'));
      selection.removeAllRanges();
      selection.addRange(range);
      $('brief-preview').focus();
      $('notice').textContent = 'Automatic copying is unavailable here. The brief is selected: use your browser’s Copy command, or download it.';
    }
  });
})();
