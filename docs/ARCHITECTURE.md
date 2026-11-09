# Architecture — what this demo actually shows

## The scenario

A policyholder's claim is denied over a coverage exclusion. The complaint
goes through five stages: Triage, Research, Response, Review, Resolve.
This demo builds out **Research** for real — the other four stages exist
as slides/narrative elsewhere in the broader project, not as running code.

## The division of labor

**Temporal owns:** durable execution only. Three concrete things, chosen
because they're the kind of work that's long-running, multi-system, and
needs to survive failure without a human watching it:
- Pulling prior complaint history
- Running an SIU fraud-signal check
- Pulling policy documents

**ServiceNow owns:** everything that needs a person, a rule, or an audit
trail. Specifically, in this demo: reflecting Temporal's progress onto a
case record, and resolving a NIGO (Not In Good Order) — a missing document
— that Temporal structurally cannot fix by retrying.

## The NIGO is the point

The third Temporal activity (`pull_policy_documents`) is written to always
fail, on purpose, simulating a missing endorsement date on the policy file.
This is NOT a transient technical failure — retrying it changes nothing,
because the data genuinely isn't there. Temporal's workflow recognizes
this, stops retrying, and pauses — waiting on a Signal rather than busy-
looping or timing out.

ServiceNow's job is to notice the pause (via the `/status` endpoint's
`nigo_flagged` field), create a task for a human to go get the missing
document, and then — once that's done — tell Temporal to resume (via the
`/resolve-nigo` endpoint, which sends a Signal).

**This is deliberately the reverse of the usual pitch.** Most "A and B
work better together" demos show the orchestration platform calling into
the workflow engine. This demo also shows the other direction: the workflow
engine getting stuck and the orchestration platform's human/task layer
getting it unstuck. That's a more concrete argument than "Temporal lacks a
case model" — it's Temporal visibly needing ServiceNow mid-execution.

## Why this maps to insurance generally, not just this one complaint

The three Research activities were deliberately chosen as genuine analogs
to a different, real public case study (a QSR company's use of Temporal
for order processing): a durable claims/complaint workflow is the analog
to an order workflow, a fraud check is the kind of per-transaction
verification step that shows up constantly in both domains, and a "missing
required data" block is universal to any regulated, document-heavy
industry. The pattern generalizes past this one demo.

## Request flow, end to end

```
ServiceNow UI Action "Check Temporal Status"
  │
  ├─ GET /complaints/{id}/status
  │    found=false → POST /complaints/{id}/start-research
  │    found=true  → update fields on the record, create task if NIGO
  │
  ▼
Gateway (FastAPI) ── Temporal client ──▶ Temporal Server (localhost:7233)
                                              │
                                              ▼
                                   ComplaintResearchWorkflow
                                   (running in the worker process)

ServiceNow Business Rule "Resolve Temporal NIGO on Document Review Complete"
  │
  ├─ fires when Document Status → IGO
  ├─ POST /complaints/{id}/resolve-nigo
  ▼
Gateway ── signal ──▶ paused Workflow resumes ──▶ completes
```
