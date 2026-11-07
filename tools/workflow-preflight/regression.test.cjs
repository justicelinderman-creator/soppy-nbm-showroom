'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const api = require('./preflight.js');
const read = name => fs.readFileSync(path.join(__dirname, 'fixtures', name), 'utf8');
let checks = 0;
function check(name, run) { run(); checks++; console.log('PASS ' + name); }
check('connected fixture: four nodes, three resolved edges, no structural errors', () => {
  const r = api.analyze(read('valid.json'));
  assert.equal(r.supported, true); assert.equal(r.complete, true);
  assert.equal(r.totals.nodes, 4); assert.equal(r.totals.resolvedConnections, 3);
  assert.equal(r.counts.error, 0); assert.equal(r.counts.review, 0);
  assert.equal(r.totals.credentialNodes, 1);
});
check('dangling sources/targets, duplicate names, and missing names/types are detected', () => {
  const codes = new Set(api.analyze(read('dangling.json')).findings.map(f => f.code));
  for (const fragment of ['DANGLING_SOURCE', 'DANGLING_TARGET', 'AMBIGUOUS_TARGET']) assert(codes.has(fragment), fragment);
  assert([...codes].some(c => c.includes('DUPLICATE')));
  assert([...codes].some(c => c.includes('NAME')));
  assert([...codes].some(c => c.includes('TYPE')));
});
check('malformed JSON and unsupported batch exports are rejected without source snippets', () => {
  const r = api.analyze(read('malformed.json'));
  assert.equal(r.parsed, false); assert(r.findings.some(f => f.code === 'INVALID_JSON'));
  assert.equal(api.analyze('[]').supported, false);
  assert.equal(api.analyze('{}').supported, false);
  assert(api.buildBrief(r).includes('not started'));
});
check('connection matching is exact and handles prototype-shaped names', () => {
  const workflow = JSON.parse('{"nodes":[{"name":"__proto__","type":"n8n-nodes-base.noOp"},{"name":"End","type":"n8n-nodes-base.noOp"}],"connections":{"__proto__":{"main":[[{"node":"End","type":"main","index":0}]]}}}');
  assert.equal(api.analyze(JSON.stringify(workflow)).totals.resolvedConnections, 1);
  workflow.connections.__proto__.main[0][0].node = 'End ';
  assert(api.analyze(JSON.stringify(workflow)).findings.some(f => f.code === 'DANGLING_TARGET'));
});
check('brief never exposes malicious names, unknown type strings, or arbitrary secrets', () => {
  const secret = 'SENTINEL_SECRET_94817';
  const malicious = '<img src=x onerror="globalThis.injected=true">' + secret;
  const r = api.analyze(JSON.stringify({name:secret,id:secret,nodes:[{name:malicious,type:secret,credentials:{[secret]:{id:secret,name:secret}},parameters:{url:secret,headers:secret,code:secret},notes:secret}],connections:{[malicious]:{main:[[{node:secret,type:secret,index:0}]]}},pinData:{a:secret}}));
  const brief = api.buildBrief(r);
  assert(!brief.includes(secret)); assert(!brief.includes('<img')); assert(!brief.includes('onerror'));
  assert(brief.includes('Node 01')); assert(r.nodes[0].credentials);
});
check('HTTP absent retry flag is a review, not a structural failure', () => {
  const r = api.analyze(JSON.stringify({nodes:[{name:'Request',type:'n8n-nodes-base.httpRequest'}],connections:{}}));
  assert.equal(r.counts.error,0); assert(r.findings.some(f => f.severity === 'review'));
});
check('UI has no HTML injection sinks, network calls, or persistent data storage', () => {
  const app = fs.readFileSync(path.join(__dirname,'app.js'),'utf8');
  for(const unsafe of [/\.innerHTML\s*=/,/\.outerHTML\s*=/,/insertAdjacentHTML\s*\(/,/\beval\s*\(/,/\bfetch\s*\(/,/XMLHttpRequest/,/localStorage/,/sessionStorage/,/sendBeacon/]) assert(!unsafe.test(app), String(unsafe));
  assert(app.includes('item.textContent = text'));
  const html = fs.readFileSync(path.join(__dirname,'index.html'),'utf8');
  assert.equal((html.match(/rel="stylesheet"/g)||[]).length,1);
  assert(html.includes("connect-src 'none'"));
  assert(html.includes('content="index,follow"'));
});
console.log('\n' + checks + ' focused regression checks passed.');
