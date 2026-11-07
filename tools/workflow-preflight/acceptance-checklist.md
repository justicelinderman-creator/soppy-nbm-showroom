# Workflow repair acceptance record

Scope reference: [identifier]  
Workflow/version: [reference]  
Environment: [test/staging/production, with authorization]  
Change reference: [commit/export/version]  
Tester and timestamp: [name; timezone]

Agree the relevant cases before work. Use **not applicable** or **not run** when accurate. Preserve actual evidence; never replace a failed result with a presumed success.

| Case | Synthetic input / starting state | Expected result | Actual result | Pass / fail / not run / N/A | Evidence reference |
| --- | --- | --- | --- | --- | --- |
| Normal input | [input] | [output] | [observed] | [status] | [reference] |
| Original failure reproduced before change | [input] | [failure] | [observed] | [status] | [reference] |
| Original failure after change | [same controlled case] | [correct behavior] | [observed] | [status] | [reference] |
| Invalid or missing input | [input] | [safe rejection or agreed result] | [observed] | [status] | [reference] |
| Transient dependency failure | [controlled failure] | [bounded behavior] | [observed] | [status] | [reference] |
| Retries exhausted | [persistent controlled failure] | [agreed stop/alert behavior] | [observed] | [status] | [reference] |
| Duplicate/replay | [same event twice within agreed boundary] | [agreed side-effect count] | [observed] | [status] | [reference] |
| Restart/concurrency, if in scope | [restart or concurrent deliveries] | [explicit expected behavior] | [observed] | [status] | [reference] |
| Rollback rehearsal, if in scope | [approved test environment] | [baseline restored] | [observed] | [status] | [reference] |

## Acceptance decision

- Required cases passed: [list]
- Failed or unperformed cases: [list]
- Known limitations: [state explicitly]
- Scope changes needed: [none or proposed change]
- Accepted by / date: [approver; timestamp]
- Revision requested: [within-scope correction, if any]

Passing a sandbox test establishes only the behavior observed under those conditions. Replay protection, restart behavior, concurrency, live integrations and production scale require their own agreed checks.
