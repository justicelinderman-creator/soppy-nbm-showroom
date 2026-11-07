/* Workflow Preflight — local structural review. No network or storage access. */
(function (root, factory) {
  'use strict';
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.WorkflowPreflight = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const LIMITS = Object.freeze({ bytes: 5 * 1024 * 1024, nodes: 2000, connections: 20000, containers: 50000 });
  const TYPES = new Map([
    ['n8n-nodes-base.manualTrigger', 'Manual Trigger'],
    ['n8n-nodes-base.webhook', 'Webhook'],
    ['n8n-nodes-base.respondToWebhook', 'Respond to Webhook'],
    ['n8n-nodes-base.scheduleTrigger', 'Schedule Trigger'],
    ['n8n-nodes-base.cron', 'Cron'],
    ['n8n-nodes-base.httpRequest', 'HTTP Request'],
    ['n8n-nodes-base.set', 'Edit Fields / Set'],
    ['n8n-nodes-base.code', 'Code'],
    ['n8n-nodes-base.function', 'Function'],
    ['n8n-nodes-base.functionItem', 'Function Item'],
    ['n8n-nodes-base.if', 'If'],
    ['n8n-nodes-base.switch', 'Switch'],
    ['n8n-nodes-base.merge', 'Merge'],
    ['n8n-nodes-base.splitInBatches', 'Loop Over Items'],
    ['n8n-nodes-base.splitOut', 'Split Out'],
    ['n8n-nodes-base.aggregate', 'Aggregate'],
    ['n8n-nodes-base.filter', 'Filter'],
    ['n8n-nodes-base.sort', 'Sort'],
    ['n8n-nodes-base.limit', 'Limit'],
    ['n8n-nodes-base.removeDuplicates', 'Remove Duplicates'],
    ['n8n-nodes-base.wait', 'Wait'],
    ['n8n-nodes-base.noOp', 'No Operation'],
    ['n8n-nodes-base.stickyNote', 'Sticky Note'],
    ['n8n-nodes-base.executeWorkflow', 'Execute Sub-workflow'],
    ['n8n-nodes-base.executeWorkflowTrigger', 'Sub-workflow Trigger'],
    ['n8n-nodes-base.errorTrigger', 'Error Trigger'],
    ['n8n-nodes-base.stopAndError', 'Stop and Error'],
    ['n8n-nodes-base.gmail', 'Gmail'],
    ['n8n-nodes-base.googleSheets', 'Google Sheets'],
    ['n8n-nodes-base.slack', 'Slack'],
    ['n8n-nodes-base.notion', 'Notion'],
    ['n8n-nodes-base.airtable', 'Airtable'],
    ['n8n-nodes-base.postgres', 'Postgres'],
    ['n8n-nodes-base.mySql', 'MySQL'],
    ['n8n-nodes-base.redis', 'Redis'],
    ['n8n-nodes-base.emailSend', 'Send Email'],
    ['n8n-nodes-base.emailReadImap', 'Email Trigger (IMAP)'],
    ['n8n-nodes-base.telegram', 'Telegram'],
    ['n8n-nodes-base.discord', 'Discord'],
    ['n8n-nodes-base.stripe', 'Stripe'],
    ['n8n-nodes-base.shopify', 'Shopify'],
    ['n8n-nodes-base.hubspot', 'HubSpot'],
    ['n8n-nodes-base.salesforce', 'Salesforce'],
    ['n8n-nodes-base.github', 'GitHub'],
    ['n8n-nodes-base.rssFeedRead', 'RSS Read'],
    ['n8n-nodes-base.rssFeedReadTrigger', 'RSS Trigger'],
    ['n8n-nodes-base.dateTime', 'Date & Time'],
    ['n8n-nodes-base.crypto', 'Crypto'],
    ['n8n-nodes-base.xml', 'XML'],
    ['n8n-nodes-base.html', 'HTML'],
    ['n8n-nodes-base.compression', 'Compression'],
    ['n8n-nodes-base.convertToFile', 'Convert to File'],
    ['n8n-nodes-base.extractFromFile', 'Extract from File'],
    ['n8n-nodes-base.readWriteFile', 'Read/Write Files'],
    ['@n8n/n8n-nodes-langchain.agent', 'AI Agent'],
    ['@n8n/n8n-nodes-langchain.lmChatOpenAi', 'OpenAI Chat Model'],
    ['@n8n/n8n-nodes-langchain.lmChatAnthropic', 'Anthropic Chat Model'],
    ['@n8n/n8n-nodes-langchain.memoryBufferWindow', 'Simple Memory'],
    ['@n8n/n8n-nodes-langchain.toolWorkflow', 'Workflow Tool']
  ]);

  const isObject = v => v !== null && typeof v === 'object' && !Array.isArray(v);
  const has = (obj, key) => Object.prototype.hasOwnProperty.call(obj, key);
  const nonempty = v => typeof v === 'string' && v.trim().length > 0;
  const alias = i => 'Node ' + String(i + 1).padStart(2, '0');
  const byteLength = text => typeof TextEncoder !== 'undefined' ? new TextEncoder().encode(text).length : text.length * 2;
  const newReport = () => ({
    formatVersion: 1, parsed: false, supported: false, complete: true, nodes: [], types: [], findings: [],
    totals: { nodes: 0, distinctTypes: 0, connectionEntries: 0, resolvedConnections: 0, disabled: 0, credentialNodes: 0, httpNodes: 0, httpRetryEnabled: 0 },
    counts: { error: 0, review: 0, info: 0 }
  });

  function analyze(text) {
    const report = newReport();
    const add = (severity, code, title, detail, nodes) => {
      report.findings.push({ severity, code, title, detail, nodes: nodes || [] });
      report.counts[severity]++;
    };
    if (typeof text !== 'string' || !text.trim()) {
      add('error', 'EMPTY_INPUT', 'There is no JSON to review', 'Choose a workflow export or paste its JSON.');
      return report;
    }
    if (byteLength(text) > LIMITS.bytes) {
      add('error', 'FILE_TOO_LARGE', 'This export exceeds the 5 MiB limit', 'Export a smaller, single workflow. Do not remove evidence from your only backup.');
      report.complete = false;
      return report;
    }
    let workflow;
    try { workflow = JSON.parse(text.charCodeAt(0) === 0xFEFF ? text.slice(1) : text); }
    catch (_) {
      add('error', 'INVALID_JSON', 'The JSON could not be parsed', 'Check for incomplete copying, trailing commas, or a non-JSON file. The parser message is withheld because it may contain source data.');
      return report;
    }
    report.parsed = true;
    if (!isObject(workflow)) {
      add('error', 'ROOT_NOT_OBJECT', 'A single workflow object is required', 'Batch arrays, .n8np packages, and other export containers are unsupported. Export one workflow as JSON from the n8n editor.');
      return report;
    }
    if (!Array.isArray(workflow.nodes)) {
      add('error', 'NODES_NOT_ARRAY', 'The export needs a nodes array', 'This may be a different file format, a wrapper around a workflow, or an incomplete export.');
      return report;
    }
    if (workflow.nodes.length > LIMITS.nodes) {
      add('error', 'TOO_MANY_NODES', 'This export exceeds the 2,000-node limit', 'Review a smaller workflow or use n8n to inspect this export. No nodes or connections were analyzed.');
      report.complete = false;
      return report;
    }
    report.supported = true;
    report.totals.nodes = workflow.nodes.length;
    if (!workflow.nodes.length) add('review', 'EMPTY_WORKFLOW', 'No nodes are present', 'An empty nodes array is readable, but it contains no workflow steps to inspect.');

    const names = new Map();
    const typeCounts = new Map();
    const unknownTypes = new Map();
    const disabled = [], credentialNodes = [], missingRetry = [], invalidRetry = [], unknown = [];
    workflow.nodes.forEach((node, i) => {
      const label = alias(i);
      const summary = { alias: label, index: i, name: null, typeLabel: 'Missing type', disabled: false, credentials: false, isHttp: false, retry: 'not applicable', incoming: 0, outgoing: 0, validObject: isObject(node) };
      report.nodes.push(summary);
      if (!summary.validObject) {
        add('error', 'INVALID_NODE', label + ' is not a node object', 'Every entry in the nodes array must be an object.', [label]);
        return;
      }
      if (!nonempty(node.name)) {
        add('error', 'MISSING_NODE_NAME', label + ' has no usable name', 'A node name must be a nonempty string so name-based connections can resolve.', [label]);
      } else {
        summary.name = node.name; // Only for optional local display; never included in buildBrief().
        if (!names.has(node.name)) names.set(node.name, []);
        names.get(node.name).push(i);
      }
      if (!nonempty(node.type)) {
        add('error', 'MISSING_NODE_TYPE', label + ' has no usable type', 'A node type must be a nonempty string. Type installation and version support are outside this review.', [label]);
      } else {
        if (!typeCounts.has(node.type)) typeCounts.set(node.type, 0);
        typeCounts.set(node.type, typeCounts.get(node.type) + 1);
        if (TYPES.has(node.type)) summary.typeLabel = TYPES.get(node.type);
        else {
          if (!unknownTypes.has(node.type)) unknownTypes.set(node.type, 'Other type ' + String(unknownTypes.size + 1).padStart(2, '0'));
          summary.typeLabel = unknownTypes.get(node.type);
          unknown.push(label);
        }
      }
      summary.disabled = node.disabled === true;
      if (summary.disabled) disabled.push(label);
      if (has(node, 'disabled') && typeof node.disabled !== 'boolean') {
        add('review', 'DISABLED_NOT_BOOLEAN', label + ' has an unusual disabled setting', 'The setting is present but is not a boolean. Only literal true is counted as disabled.', [label]);
      }
      summary.credentials = isObject(node.credentials) && Object.keys(node.credentials).length > 0;
      if (summary.credentials) credentialNodes.push(label);
      if (has(node, 'credentials') && !isObject(node.credentials)) {
        add('review', 'CREDENTIALS_SHAPE', label + ' has an unusual credential-reference field', 'The credentials field is present but is not an object. No credential field values are displayed or exported.', [label]);
      }
      summary.isHttp = node.type === 'n8n-nodes-base.httpRequest';
      if (summary.isHttp) {
        report.totals.httpNodes++;
        summary.retry = node.retryOnFail === true ? 'enabled in export' : 'not enabled in export';
        if (node.retryOnFail === true) report.totals.httpRetryEnabled++;
        else missingRetry.push(label);
        if (has(node, 'retryOnFail') && typeof node.retryOnFail !== 'boolean') invalidRetry.push(label);
      }
    });
    for (const indexes of names.values()) {
      if (indexes.length > 1) add('error', 'DUPLICATE_NODE_NAME', 'Multiple nodes share the same name', 'Name-based connection resolution is ambiguous. Inspect these nodes in the original export before changing any links.', indexes.map(alias));
    }
    report.totals.distinctTypes = typeCounts.size;
    for (const [type, count] of typeCounts) report.types.push({ label: TYPES.get(type) || unknownTypes.get(type), count });
    report.types.sort((a, b) => b.count - a.count || a.label.localeCompare(b.label));
    report.totals.disabled = disabled.length;
    report.totals.credentialNodes = credentialNodes.length;
    if (disabled.length) add('review', 'DISABLED_NODES', 'Disabled nodes need a quick intent check', 'These nodes are marked disabled. Confirm that this is intentional; a disabled node is not automatically a defect.', disabled);
    if (credentialNodes.length) add('info', 'CREDENTIAL_REFERENCES', 'Credential references are present', 'Only their presence was counted. Credential IDs, names, values, access, and validity were not inspected or exported.', credentialNodes);
    if (missingRetry.length) add('review', 'HTTP_RETRY_REVIEW', 'Review the HTTP retry policy', 'retryOnFail is not literal true on these HTTP Request nodes. This can be intentional. Check idempotency, provider limits, backoff, and error handling before enabling retries; repeating a write can duplicate its effect.', missingRetry);
    if (invalidRetry.length) add('review', 'HTTP_RETRY_SHAPE', 'An HTTP retry flag has an unusual shape', 'retryOnFail is present but is not a boolean. Review it in the matching n8n version.', invalidRetry);
    if (unknown.length) add('info', 'OTHER_TYPES', 'Some node types are shown as aliases', 'Unrecognized and community node-type strings are grouped under Other type aliases to avoid exposing arbitrary text. Their availability and compatibility were not checked.', unknown);

    if (has(workflow, 'connections') && !isObject(workflow.connections)) {
      add('error', 'CONNECTIONS_NOT_OBJECT', 'The connections field is not an object', 'Connections must be a source-name keyed object. No connections were analyzed.');
    } else {
      const connections = workflow.connections || {};
      let containers = 0, exceeded = false;
      const consume = () => { if (++containers > LIMITS.containers) { exceeded = true; return false; } return true; };
      outer: for (const [sourceName, channels] of Object.entries(connections)) {
        if (!consume()) break;
        const group = containers;
        const sourceIndexes = names.get(sourceName) || [];
        const sourceLabel = sourceIndexes.length === 1 ? alias(sourceIndexes[0]) : 'Connection source group ' + group;
        const sourceAliases = sourceIndexes.map(alias);
        if (!sourceIndexes.length) add('error', 'DANGLING_SOURCE', 'A connection source has no matching node', sourceLabel + ' uses a source name that is absent from the nodes array. The original name is withheld.');
        else if (sourceIndexes.length > 1) add('error', 'AMBIGUOUS_SOURCE', 'A connection source matches multiple nodes', 'The source name is duplicated, so outgoing connections cannot be resolved uniquely.', sourceAliases);
        if (!isObject(channels)) {
          add('error', 'INVALID_CHANNEL_MAP', 'A source has a malformed connection map', sourceLabel + ' needs an object containing output-channel arrays.', sourceAliases);
          continue;
        }
        let channelOrdinal = 0;
        for (const outputs of Object.values(channels)) {
          channelOrdinal++;
          if (!consume()) break outer;
          if (!Array.isArray(outputs)) {
            add('error', 'INVALID_OUTPUTS', 'A connection channel is not an array', sourceLabel + ', channel ' + channelOrdinal + ': expected an array of output lists.', sourceAliases);
            continue;
          }
          for (let outputIndex = 0; outputIndex < outputs.length; outputIndex++) {
            if (!consume()) break outer;
            const targets = outputs[outputIndex];
            if (!Array.isArray(targets)) {
              add('error', 'INVALID_TARGET_LIST', 'An output does not contain a target list', sourceLabel + ', channel ' + channelOrdinal + ', output ' + outputIndex + ': expected an array.', sourceAliases);
              continue;
            }
            for (let targetIndex = 0; targetIndex < targets.length; targetIndex++) {
              if (report.totals.connectionEntries >= LIMITS.connections) { exceeded = true; break outer; }
              report.totals.connectionEntries++;
              const target = targets[targetIndex];
              const where = sourceLabel + ', channel ' + channelOrdinal + ', output ' + outputIndex + ', target ' + (targetIndex + 1);
              if (!isObject(target) || !nonempty(target.node)) {
                add('error', 'INVALID_TARGET', 'A connection has no usable target node name', where + ': expected an object with a nonempty node string.', sourceAliases);
                continue;
              }
              const targetIndexes = names.get(target.node) || [];
              if (!targetIndexes.length) add('error', 'DANGLING_TARGET', 'A connection points to a missing node', where + ': the target name is absent from the nodes array. The original name is withheld.', sourceAliases);
              else if (targetIndexes.length > 1) add('error', 'AMBIGUOUS_TARGET', 'A connection target matches multiple nodes', where + ': the target name is duplicated.', targetIndexes.map(alias));
              const shapeOkay = nonempty(target.type) && Number.isInteger(target.index) && target.index >= 0;
              if (!shapeOkay) add('error', 'INVALID_EDGE_FIELDS', 'A connection has invalid type or index fields', where + ': type must be a nonempty string and index a nonnegative integer. Actual port compatibility is not checked.', [...sourceAliases, ...targetIndexes.map(alias)]);
              if (sourceIndexes.length === 1 && targetIndexes.length === 1) {
                report.nodes[sourceIndexes[0]].outgoing++;
                report.nodes[targetIndexes[0]].incoming++;
                if (shapeOkay) report.totals.resolvedConnections++;
              }
            }
          }
        }
      }
      if (exceeded) {
        report.complete = false;
        add('error', 'CONNECTION_LIMIT', 'The connection scan reached its limit', 'Only a partial scan is available. Limits: 20,000 connection entries or 50,000 source/channel/output containers. Use n8n to inspect the complete export.');
      }
    }
    report.findings.sort((a, b) => ({ error: 0, review: 1, info: 2 }[a.severity]) - ({ error: 0, review: 1, info: 2 }[b.severity]));
    return report;
  }

  function status(report) {
    if (!report.parsed) return 'JSON not reviewed';
    if (!report.supported) return 'Unsupported workflow structure';
    if (!report.complete) return 'Partial structural review';
    if (report.counts.error) return 'Structural issues need attention';
    if (report.counts.review) return 'No blocking structural findings; review settings';
    return 'No blocking structural findings detected';
  }

  function buildBrief(report) {
    if (!report || !report.totals || !report.findings) throw new TypeError('A report from analyze() is required.');
    const t = report.totals;
    const lines = [
      '# Workflow Preflight — support brief', '',
      'Prepared with Cosie Workflow Preflight. Structural review only.', '',
      '## Result', '', status(report), '',
      '- JSON parsed: ' + (report.parsed ? 'yes' : 'no'),
      '- Supported single-workflow shape: ' + (report.supported ? 'yes' : 'no'),
      '- Scan coverage: ' + (!report.supported ? 'not started — see findings' : report.complete ? 'complete within the supported checks' : 'incomplete — see findings'),
      '- Node entries: ' + t.nodes,
      '- Distinct nonempty node types: ' + t.distinctTypes,
      '- Connection entries inspected: ' + t.connectionEntries,
      '- Connections with unique endpoints and basic fields: ' + t.resolvedConnections,
      '- Disabled nodes (literal true): ' + t.disabled,
      '- Nodes with nonempty credential-reference objects: ' + t.credentialNodes,
      '- HTTP Request nodes: ' + t.httpNodes,
      '- HTTP Request nodes with retryOnFail=true: ' + t.httpRetryEnabled,
      '- Findings: ' + report.counts.error + ' structural, ' + report.counts.review + ' review, ' + report.counts.info + ' informational', '',
      '## Findings', ''
    ];
    if (!report.findings.length) lines.push('No findings from the supported checks. This does not establish that the workflow works.');
    for (const f of report.findings) {
      lines.push('### ' + ({ error: 'STRUCTURAL', review: 'REVIEW', info: 'INFO' }[f.severity]) + ' · ' + f.code, '', f.title + '.', '', f.detail);
      if (f.nodes.length) lines.push('', 'Node aliases: ' + f.nodes.join(', ') + '.');
      lines.push('');
    }
    if (report.types.length) {
      lines.push('## Type inventory', '', '| Type label | Nodes |', '| --- | ---: |');
      for (const row of report.types) lines.push('| ' + row.label + ' | ' + row.count + ' |');
      lines.push('');
    }
    if (report.nodes.length) {
      lines.push('## Node inventory', '', 'Aliases follow the nodes array order in the original export (Node 01 is the first entry). Original names are always omitted from this brief.', '', '| Alias | Type label | Disabled | Credential references | In / out entries | HTTP retry flag |', '| --- | --- | --- | --- | --- | --- |');
      for (const node of report.nodes) lines.push('| ' + node.alias + ' | ' + node.typeLabel + ' | ' + (node.disabled ? 'yes' : 'no') + ' | ' + (node.credentials ? 'present' : 'not detected') + ' | ' + node.incoming + ' / ' + node.outgoing + ' | ' + node.retry + ' |');
      lines.push('', 'In / out counts include entries with uniquely matching endpoint names; they do not certify valid execution ports.');
    }
    lines.push('', '## Context to add before requesting support', '',
      '- Intended outcome: [add a short, non-sensitive description]',
      '- Expected behavior: [what should happen]',
      '- Observed behavior: [what actually happened]',
      '- n8n version and hosting mode: [add if known]',
      '- Last known successful run and first failure: [time + timezone]',
      '- Recent change: [one sentence]',
      '- Reproduction steps using synthetic data: [steps]',
      '- Acceptance check: [observable pass condition]',
      '- Rollback owner and backup location: [reference, not credentials]', '',
      '## Privacy and limits', '',
      'The original file is processed in this browser tab. The review sends no workflow data over the network and uses no analytics, external dependencies, or browser storage. Copying or downloading a brief happens only when requested.', '',
      'This brief is constructed from counts, fixed check descriptions, known type labels, and ordinal aliases. It omits workflow names and IDs, filenames, original node names, unknown raw type strings, credential identifiers and values, parameters, URLs, headers, code, expressions, pinned data, and execution data. It is not a sanitizer for the original export. Review even this brief before sharing; counts and known integration labels may reveal business context.', '',
      'This tool does not import or execute a workflow, access n8n, test credentials, check connectivity, inspect parameter expressions or code, validate node versions or installed packages, prove port compatibility or reachability, detect all secrets, certify security, establish production readiness, or guarantee a fix. Presence or absence of a retry flag alone is not a reliability verdict. Retries may duplicate side effects.', '',
      'Supported input: one editor-exported workflow JSON object with a nodes array; maximum 5 MiB and 2,000 nodes. Connection scan stops at 20,000 entries or 50,000 containers and is explicitly marked partial. Batch exports, .n8np packages, and runtime execution exports are outside scope.', '',
      '## Primary references', '',
      '- n8n — Export and import workflows: https://docs.n8n.io/workflows/export-import/',
      '- n8n — Node settings (including Retry On Fail and deactivation): https://docs.n8n.io/workflows/components/nodes/', '',
      'Free launch resource from Cosie. No repair, monitoring, or support service is included or automatically started.', ''
    );
    return lines.join('\n');
  }

  return Object.freeze({ analyze, buildBrief, status, LIMITS });
});
