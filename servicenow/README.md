# ServiceNow setup — wiring to the Temporal gateway

This folder documents (it does not auto-install — ServiceNow config isn't
something you can "run" from outside the instance) what was built on the
ServiceNow side to talk to the Temporal gateway in `../temporal/`.

You'll need admin access to a ServiceNow instance and the gateway from
`../temporal/` already running and reachable (see its README for the
ngrok/tunnel step if you're running it locally rather than on a server
with a public address).

## 1. Add the fields

See `fields_reference.md` for the exact list. Add these to your
complaint/case table via Studio or **System Definition > Tables**.

## 2. Create the System Property

Navigate to `sys_properties.list` → **New**:
- Name: `x_temporal.gateway_url`
- Type: string
- Value: your gateway's current public URL (no trailing slash)

**This value changes** if you're using a tunnel like ngrok and it gets
restarted (unless you're on a plan with a static subdomain) — update it
before each session if needed.

## 3. Create the UI Action

Navigate to `sys_ui_action.list` → **New**. Use the settings in the comment
header of `ui_action_check_temporal_status.js`, and paste that file's
contents into the Script field.

**Before using it:** the script references field names like
`u_fraud_check_complete` — make sure these match what you actually created
in step 1, and adjust `current.u_policy_number` (used when auto-starting a
workflow) to whatever your table's actual policy-number field is called,
or remove that line if you don't have one.

## 4. Create the Business Rule

Navigate to `sys_script.list` → **New**. Use the settings in the comment
header of `business_rule_resolve_nigo.js` (when: after, update only,
condition: your document-status field changes to your "resolved" choice
value), and paste that file's contents into the Script field.

## 5. Test it

1. Confirm the gateway is reachable: visit
   `<your gateway URL>/health` in a browser — expect `{"status":"ok"}`
2. Open any complaint record that hasn't been used yet
3. Click the UI Action button once → it should auto-start a Temporal
   workflow and tell you to check again shortly
4. Wait a few seconds, click it again → fields populate, a task appears
   for the missing document (the NIGO)
5. Mark the document reviewed and flip the status field to your
   "resolved" value, save → the Business Rule fires and signals Temporal
6. Click the UI Action one more time → the NIGO should now show resolved

See `../docs/DEMO_SCRIPT.md` for the full narrated walkthrough, and
`../docs/TROUBLESHOOTING.md` if any step doesn't match what's expected.

## A note on Workspace visibility

If you're using Configurable Workspace (CWF) rather than the classic UI,
a newly created UI Action sometimes doesn't appear immediately — check the
`...` overflow menu next to your other form buttons, and hard-refresh the
tab, before assuming it's misconfigured. If it's still missing after that,
check the UI Action's `Order` field, and whether the Workspace experience's
page in UI Builder is configured to show a curated action list rather than
"all eligible UI actions."
