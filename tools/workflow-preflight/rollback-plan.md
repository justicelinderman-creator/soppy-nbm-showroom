# Workflow rollback plan

Scope reference: [identifier]  
Change owner: [name/role]  
Authorized rollback operator: [name/role]  
Approved change window: [date/timezone]

## Baseline and recovery materials

- Baseline workflow export: [private file/version reference]
- Relevant configuration backup: [private reference; never credentials in this document]
- Prior activation state and trigger behavior: [record]
- External side effects to watch: [records, messages, charges, files]
- Any state that an export alone does not restore: [queues, deduplication store, external records]

## Rollback triggers

| Trigger | Observable threshold | Decision owner |
| --- | --- | --- |
| Original failure persists | [specific condition] | [owner] |
| Unexpected side effect | [specific condition] | [owner] |
| Required acceptance case fails | [case] | [owner] |
| Other | [condition] | [owner] |

## Agreed rollback sequence

1. [Notify the owner and record the incident/time.]
2. [Stop or isolate new runs using the approved method; account for in-flight executions.]
3. [Restore the agreed baseline and activation state.]
4. [Run the agreed recovery check in the authorized environment.]
5. [Reconcile any external side effects through a separately authorized action.]
6. [Record the result, unresolved issues and next decision.]

Do not assume restoring a workflow reverses an email, charge, record update or other external side effect. Define those recovery actions separately.

## Recovery record

- Trigger observed: [facts and time]
- Steps actually performed: [record]
- Recovery check result: [evidence]
- External reconciliation needed: [details]
- Current workflow state: [active/inactive/other]
- Owner informed and next action: [record]
