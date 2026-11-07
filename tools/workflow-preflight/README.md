# Cosie Workflow Rescue Kit

Version 1.0 · November 7, 2026 · Free launch resource

Use Workflow Preflight to review the structure of an n8n JSON export, then use the included templates to define a repair and document its acceptance and handoff.

## Start in two minutes

1. Open `index.html` in a modern browser. The included HTML, CSS and JavaScript work together; keep them in the same folder.
2. Try an included synthetic example before selecting your own export.
3. Select or paste one workflow JSON export. Review the structural findings and advisory settings.
4. Copy or download the redacted support brief. Read it before sharing it.
5. Use the blank templates below to describe the intended result and agree what a successful repair means.

Online tool: https://justicelinderman-creator.github.io/soppy-nbm-showroom/tools/workflow-preflight/

## Included files

- `index.html`, `styles.css`, `app.js`, `preflight.js`, `samples.js`: the browser tool.
- `fixtures/valid.json`: synthetic structurally valid example, not a tested production workflow.
- `fixtures/dangling.json`: synthetic example with structural problems for demonstration.
- `fixtures/malformed.json`: deliberately invalid JSON for error handling.
- `incident-intake.md`: capture one reproducible failure without exposing credentials.
- `acceptance-checklist.md`: agree concrete cases and record their actual results.
- `rollback-plan.md`: define backup, rollback triggers and the responsible person.
- `handoff-template.md`: record the agreed change, artifacts, evidence and limitations.

## What the tool checks

The inspector reviews a single workflow object and its nodes/connections. Checks include missing node fields, duplicate names, invalid connection structures, missing connection endpoints, disabled nodes, credential-reference presence and an advisory HTTP retry review. Findings describe structure and selected settings; they are not a complete n8n schema validator.

Input limits: 5 MiB, 2,000 nodes, 20,000 connection entries and 50,000 scanned connection containers. A scan reaching a limit is labeled incomplete. Batch exports, execution histories and packaged workflows are outside scope.

## Privacy

The workflow review runs in your browser. The tool does not upload export contents, contact n8n, collect analytics or save workflow data in browser storage. The web version loads its own page assets. Selecting or pasting a file does not send it to Cosie.

The support brief is assembled from fixed descriptions, counts, known type labels and ordinal node aliases. It omits original names, arbitrary type strings, credential identifiers/values, parameters, code, expressions and execution data. It does not sanitize or replace the original export. Even the redacted brief can reveal context through counts and known integration names; review it before sharing.

Closing the tab discards the in-memory review. Copies and downloads you choose to create remain wherever you save them.

## What this does not establish

The tool does not execute or import a workflow, verify credentials, validate expressions, audit code, certify security, confirm installed node versions or prove production behavior. A structurally clean result does not prove the workflow works. A retry flag by itself is not a reliability verdict; retries can repeat side effects. Do not deploy the synthetic fixtures into production.

## Using the templates

Copy each blank template for a specific job. Replace bracketed prompts with accurate details. Record skipped and failed checks as such. Store sensitive evidence privately and reference it by an internal identifier instead of inserting secrets into a shared handoff.

The templates may be used and adapted for your own workflow reviews and client handoffs. The package does not grant rights to third-party data, n8n trademarks or customer files. Cosie is independent and does not claim n8n endorsement. No repair, monitoring or support service is included automatically.

## Optional scoped help

The $200 n8n Workflow Reliability Pilot covers one agreed failure class in one existing workflow, a sanitized export, relevant acceptance checks, rollback notes and one revision within scope. Fit, scope, delivery date, total price and payment/refund terms are agreed in writing before payment.

Service details and brief: https://justicelinderman-creator.github.io/soppy-nbm-showroom/services/n8n/#brief

## Primary references

- n8n export/import: https://docs.n8n.io/workflows/export-import/
- n8n node settings: https://docs.n8n.io/workflows/components/nodes/
