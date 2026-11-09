# Demo script — the narrated click-through

Assumes all three Temporal-side processes are already running (see
`../temporal/README.md`) and the ServiceNow pieces are already configured
(see `../servicenow/README.md`).

## 1. Open a fresh complaint record

Pick one that's never been through this flow before — avoids confusing a
stale state for a bug.

## 2. Click "Check Temporal Status" — first time

**What happens:** an info message saying research has started, and to
check again shortly. Nothing on the form changes yet.

**What to say:** "Temporal's now durably pulling the complaint history and
running the fraud-signal check in the background — this is exactly the
kind of long-running, multi-system job it's built for."

## 3. Wait a few seconds

**What to say, to fill the pause naturally:** "This step hits three
different systems — complaint history, fraud check, and the policy
document store. Whatever responds slowest decides this step's length."

## 4. Click "Check Temporal Status" — second time

**What happens:** Fraud Check and Claim History checkboxes tick, fraud
risk score populates, Document Status shows `NIGO-Missing Documents`, and
a task appears.

**What to say:** "Temporal hit a problem it genuinely can't solve on its
own — the endorsement date just isn't in the file. Retrying wouldn't help;
that's not what's broken. So it's paused, and it's waiting."

## 5. Resolve the NIGO

Check **Document Review Complete**, set **Document Status** to **IGO**,
save.

**What happens:** a Business Rule fires silently and signals Temporal.

**What to say:** "The instant someone here confirms the document's in
hand, Temporal resumes — no restart, no re-running the steps that already
succeeded."

## 6. Click "Check Temporal Status" one more time

**What happens:** `nigo_resolved` now shows true.

## 7. (Optional, if there's time or interest) Show the Temporal Web UI directly

`http://localhost:8233` → click into the workflow → show it as
**Completed**. This is the most concrete proof available, since it comes
straight from Temporal's own system of record, not anything ServiceNow is
reporting about itself.

---

## If something looks wrong mid-demo

Don't improvise a fix live. Say something like "let's come back to that"
and move on — see `TROUBLESHOOTING.md` afterward. The most common causes,
roughly in order of likelihood: the gateway or worker process isn't
running anymore, the tunnel URL changed and the system property wasn't
updated, or the record you picked was already used in an earlier test run.
