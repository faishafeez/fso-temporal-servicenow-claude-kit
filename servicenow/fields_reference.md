# Fields added to the complaint/case table

Demo table used: `u_insurance_complaint_case`. Adjust names to fit your own
table — these are just the ones referenced by the two scripts in this folder.

| Label | Type | Name used in scripts | Notes |
|---|---|---|---|
| Fraud Check Complete | True/False | `u_fraud_check_complete` | Set by the UI Action from `fraud_check_done` |
| Fraud Risk Score | Choice (Low, Medium, High) | `u_fraud_risk_score` | Set from `fraud_risk_score`, mapped from lowercase to the choice labels |
| Claim History Reviewed | True/False | `u_claim_history_reviewed` | Set from `complaint_history_done` |
| Document Review Complete | True/False | `u_document_review_complete` | Set from `document_review_complete`; also the field a human checks to help trigger resolution |
| Document Status | Choice (NIGO-Missing Documents, NIGO-Wrong Information, IGO) | `u_document_status` | Set from `document_status`; **changing this to IGO is what the Business Rule watches for** |

## System Property

| Name | Type | Value |
|---|---|---|
| `x_temporal.gateway_url` | string | Your gateway's reachable URL, e.g. `https://your-tunnel.ngrok-free.dev` — no trailing slash |

## Not included in this demo, worth adding for a real build

- A guard field (e.g. `u_nigo_task_created`, True/False) to stop the UI
  Action from creating a second task if clicked again after a task already
  exists for the same NIGO.
- A link from the created task back to the parent complaint record
  (the demo creates a plain `task` record with no `parent` reference set —
  intentional, to avoid assuming your task table's exact relationship
  field, but worth wiring up for anything beyond a demo).
