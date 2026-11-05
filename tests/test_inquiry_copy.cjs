const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../assets/inquiry.js'), 'utf8');

async function checkFailure(clipboard) {
  const status = {textContent: ''};
  const field = {readOnly: true, value: 'justice.linderman@gmail.com', focused: false, selected: false,
    focus() { this.focused = true; }, select() { this.selected = true; }};
  const button = {hidden: true, dataset: {copyTarget: 'inquiry-address', copyName: 'Email address'},
    addEventListener(type, listener) { assert.equal(type, 'click'); this.activate = listener; }};
  const box = {querySelectorAll() { return [button]; }};
  const elements = {'email-options': box, 'inquiry-copy-status': status, 'inquiry-address': field};
  vm.runInNewContext(source, {document: {getElementById(id) { return elements[id]; }}, navigator: {clipboard}});
  assert.equal(button.hidden, false);
  await button.activate();
  assert.equal(field.focused, true);
  assert.equal(field.selected, true);
  assert.match(status.textContent, /Automatic copying is unavailable/);
  assert.match(status.textContent, /Nothing has been sent/);
  assert.doesNotMatch(status.textContent, /copied\./);
}

(async () => {
  await checkFailure({writeText: async () => { throw new Error('Clipboard denied'); }});
  await checkFailure(undefined);
  console.log(JSON.stringify({passed: true, failure_cases: 2, cases: ['clipboard promise rejected', 'clipboard API absent']}));
})().catch(error => { console.error(error); process.exitCode = 1; });
