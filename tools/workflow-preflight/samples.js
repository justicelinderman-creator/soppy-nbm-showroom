/* Synthetic fixtures embedded so sample loading also works without a web server. */
window.PreflightSamples = Object.freeze({
  valid: JSON.stringify({
    name: 'Synthetic: example inventory request',
    nodes: [
      { name: 'Run example', type: 'n8n-nodes-base.manualTrigger', typeVersion: 1, position: [0, 0], parameters: {} },
      { name: 'Read example data', type: 'n8n-nodes-base.httpRequest', typeVersion: 4.2, position: [260, 0], retryOnFail: true, maxTries: 3, waitBetweenTries: 1500, credentials: { httpHeaderAuth: { id: 'SYNTHETIC_ONLY', name: 'Example credential reference' } }, parameters: { url: 'https://example.invalid/inventory' } },
      { name: 'Pick example fields', type: 'n8n-nodes-base.set', typeVersion: 3.4, position: [520, 0], parameters: {} },
      { name: 'Finish example', type: 'n8n-nodes-base.noOp', typeVersion: 1, position: [780, 0], parameters: {} }
    ],
    connections: {
      'Run example': { main: [[{ node: 'Read example data', type: 'main', index: 0 }]] },
      'Read example data': { main: [[{ node: 'Pick example fields', type: 'main', index: 0 }]] },
      'Pick example fields': { main: [[{ node: 'Finish example', type: 'main', index: 0 }]] }
    },
    active: false,
    settings: {}
  }, null, 2),
  dangling: JSON.stringify({
    name: 'Synthetic: broken connections for review',
    nodes: [
      { name: 'Start example', type: 'n8n-nodes-base.manualTrigger', parameters: {}, position: [0, 0] },
      { name: 'Repeated example name', type: 'n8n-nodes-base.httpRequest', disabled: true, parameters: { url: 'https://example.invalid' }, position: [260, 0] },
      { name: 'Repeated example name', type: 'n8n-nodes-base.set', parameters: {}, position: [520, 0] },
      { type: 'n8n-nodes-base.noOp', parameters: {}, position: [780, 0] },
      { name: 'Type missing here', parameters: {}, position: [1040, 0] }
    ],
    connections: {
      'Start example': { main: [[{ node: 'Deleted example node', type: 'main', index: 0 }, { node: 'Repeated example name', type: 'main', index: 0 }]] },
      'Removed example source': { main: [[{ node: 'Start example', type: 'main', index: 0 }]] }
    },
    active: false
  }, null, 2),
  malformed: '{\n  "name": "Synthetic malformed example",\n  "nodes": [\n    { "name": "Example node", "type": "n8n-nodes-base.noOp" },\n  ],\n  "connections": {}\n}'
});
