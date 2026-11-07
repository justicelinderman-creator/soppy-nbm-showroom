# Workflow incident intake

Use one copy for one reproducible failure. Keep API keys, tokens, passwords, private customer records and complete production exports out of shared intake messages.

## Scope reference

- Reference: [short identifier]
- Requester and approver: [names/roles]
- Workflow purpose: [one sentence]
- n8n version and hosting mode: [version; cloud/self-hosted]
- Available test environment: [describe]
- Preferred timing: [date/timezone or flexible]

## Expected and observed behavior

- Trigger/input: [sanitized or synthetic example]
- Expected behavior: [specific output or side effect]
- Observed behavior: [what happened]
- Frequency and impact: [known frequency; what is affected]
- Last known successful run: [time/timezone or unknown]
- First known failure: [time/timezone or unknown]
- Recent change: [facts, or unknown]

## Reproduction

1. [Prepare synthetic input and starting state.]
2. [Perform one action.]
3. [Record the observed result and exact relevant error, redacted.]

- Evidence reference: [private log/screenshot location; no credentials]
- Can the failure be reproduced outside production? [yes/no/unknown]
- External services involved: [service names only]
- Duplicate/replay risk: [what could be created or charged twice?]

## Proposed boundary

- One failure class to address: [define it]
- Intended change: [proposed approach, subject to review]
- Outside this scope: [new features, other failure classes, infrastructure, monitoring]
- Acceptance condition: [observable pass/fail statement]
- Access and deployment owner: [who authorizes and performs changes]

## Before work

- [ ] The owner approved the scope and access required.
- [ ] The baseline export and relevant configuration are backed up privately.
- [ ] Acceptance cases and rollback triggers are agreed.
- [ ] Delivery timing, price, revision allowance and payment/refund terms are recorded.

An intake is a request for scoping. It is not a diagnosis, completed repair or agreement to pay.
