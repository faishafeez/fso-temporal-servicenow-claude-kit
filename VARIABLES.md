# Variables Reference — All placeholders explained

Use this to understand what each variable means and where to get it. These appear throughout the setup docs, scripts, and configuration.

---

## ServiceNow Instance

| Variable | Example | Where to find it | Used in |
|---|---|---|---|
| `YOUR_INSTANCE_URL` | `https://democrmffsoinsurancealectriau154341.service-now.com` | Copy from your browser address bar | `temporal/gateway.py`, `servicenow/ui_action_check_temporal_status.js`, `03_claude-setup/` scripts |
| `YOUR_INSTANCE_NAME` | `democrmffsoinsurancealectriau154341` | Extract from URL (part before `.service-now.com`) | OAuth client setup, MCP server config |

---

## ServiceNow Table & Fields

| Variable | Example | Where to find it | Used in | Notes |
|---|---|---|---|---|
| `YOUR_TABLE_NAME` | `u_insurance_complaint_case` | Your ServiceNow instance → create or identify the table you want to use | `servicenow/fields_reference.md`, UI Action, Business Rule | Field names in scripts must match what you actually create |
| `YOUR_POLICY_FIELD` | `u_policy_number` | The field on your table that stores the customer's policy number | `servicenow/ui_action_check_temporal_status.js` line: `current.u_policy_number` | Used by the UI Action to auto-start workflows |
| `YOUR_CONSUMER_FIELD` | `consumer` or `customer_id` | The field that links a record to a customer | All scripts and queries | Must match your actual table structure |

**Field names from the demo table** (adjust these to match your table):
- Fraud Check Complete: `u_fraud_check_complete` (True/False)
- Fraud Risk Score: `u_fraud_risk_score` (Choice: Low, Medium, High)
- Claim History Reviewed: `u_claim_history_reviewed` (True/False)
- Document Review Complete: `u_document_review_complete` (True/False)
- Document Status: `u_document_status` (Choice: NIGO-Missing Documents, IGO)

---

## Temporal

| Variable | Example | Where to find it | Used in | Notes |
|---|---|---|---|---|
| `TEMPORAL_SERVER_ADDRESS` | `localhost:7233` | Run `temporal server start-dev` (uses this by default) | `temporal/worker.py`, `temporal/gateway.py` | For local dev; change if running Temporal in cloud |
| `TEMPORAL_NAMESPACE` | `default` | Default Temporal namespace | `temporal/worker.py`, `temporal/gateway.py` | Can customize per deployment |
| `TASK_QUEUE_NAME` | `complaint-research-task-queue` | Defined in `temporal/worker.py` | `temporal/gateway.py`, `temporal/starter_client.py` | Workers listen on this; gateway sends tasks here |

---

## Temporal ↔ ServiceNow Gateway

| Variable | Example | Where to find it | Used in | Notes |
|---|---|---|---|---|
| `GATEWAY_URL` | `http://localhost:8000` (local) or `https://your-tunnel.ngrok-free.dev` (public) | Run `uvicorn gateway:app --port 8000` to find local; use ngrok for public | `servicenow/ui_action_check_temporal_status.js`, system property `x_temporal.gateway_url`, `03_claude-setup/` scripts | **Must be reachable from ServiceNow** — if on localhost, use ngrok tunnel |
| `GATEWAY_PORT` | `8000` | Configured in `uvicorn` command | `temporal/gateway.py` startup | Ensure no other process uses this port |

---

## OAuth & Authentication (ServiceNow → Anthropic)

| Variable | Example | Where to find it | Used in | Notes |
|---|---|---|---|---|
| `YOUR_CLIENT_ID` | `a1c7b931e2bd4342a372b54bb3b9e131` | ServiceNow → Machine Identity Console → OAuth Integrations → Inbound → Your integration → Client ID | `03_claude-setup/mint-token.sh` | 32-character hex string |
| `YOUR_CLIENT_SECRET` | `T*1(d:RLkq)9*n0;F'...` | Same location as Client ID (confidential) | `03_claude-setup/mint-token.sh` | Keep this secret; use single quotes in shell scripts to protect special characters |
| `YOUR_ANTHROPIC_API_KEY` | `sk-ant-v0-...` | https://console.anthropic.com → API Keys | `03_claude-setup/` setup, stored in ServiceNow system property | Keep this secret; never commit to git |
| `YOUR_VAULT_ID` | `vlt_011Cg4neN4eg3tLt7GPs4bDp` | Anthropic console → Vaults → Create or identify your vault → Vault ID | `03_claude-setup/rotate-vault.js` | Format: `vlt_` followed by 24 alphanumeric characters |

---

## OAuth Token (Temporal Research Workflow → ServiceNow)

| Variable | Example | Where to find it | Used in | Notes |
|---|---|---|---|---|
| `NEW_JWT_TOKEN` | `eyJraWQiOiI...` (very long string with 3 dot-separated segments) | Run `03_claude-setup/mint-token.sh` → copy `access_token` from output | `03_claude-setup/rotate-vault.js` | Must have exactly 3 segments (header.payload.signature) to be valid |
| `TOKEN_LIFESPAN` | `31535999` (seconds) | Configured in ServiceNow OAuth client settings → Token Format / Lifetime | `03_claude-setup/mint-token.sh` output → check `expires_in` | Longer is better; suggested: 1 year (31,535,999 seconds) |
| `CREDENTIAL_ID` | `vcrd_018gaak3eCWLHwQxpWnMepES` | Run `03_claude-setup/rotate-vault.js` → check logs for `VAULT_CRED_CREATE_BODY` → copy `id` field | `03_claude-setup/` (for next rotation) | Format: `vcrd_` followed by 24 alphanumeric characters; save this for next time |

---

## System Properties (ServiceNow)

Create these in **System Definition > Properties**:

| Property Name | Value | Used by | Notes |
|---|---|---|---|
| `x_temporal.gateway_url` | Your `GATEWAY_URL` | `servicenow/ui_action_check_temporal_status.js`, `servicenow/business_rule_resolve_nigo.js` | No trailing slash; update if using ngrok and the tunnel restarts |
| `x_snc_insuranct8ex.claude_api_key` | Your `YOUR_ANTHROPIC_API_KEY` | `03_claude-setup/rotate-vault.js` (read via `gs.getProperty()`) | Type: password2; encrypted in database |

---

## Claude Desktop / MCP

| Variable | Example | Where to find it | Used in | Notes |
|---|---|---|---|---|
| `SERVICENOW_INSTANCE_URL` | Same as `YOUR_INSTANCE_URL` | Your instance URL | `claude_desktop_config.json` → MCP server env | Used by Claude Desktop to authenticate to ServiceNow |
| `SERVICENOW_CLIENT_ID` | Same as `YOUR_CLIENT_ID` | OAuth client | `claude_desktop_config.json` | Allows Claude Code to create/read records |
| `SERVICENOW_CLIENT_SECRET` | Same as `YOUR_CLIENT_SECRET` | OAuth client | `claude_desktop_config.json` | Allows Claude Code to create/read records |
| `MCP_SERVER_URL` | `https://democrmffsoinsurancealectriau154341.service-now.com/sncapps/mcp-server/mcp/sn_mcp_server_default` | Your instance URL + fixed path | `03_claude-setup/rotate-vault.js` | Used to bind the credential to this specific MCP server endpoint |

---

## Quick substitution checklist

Before you start Phase 2 or 3, fill these in:

```
Instance URL:                 ___________________________________
Instance Name:                ___________________________________
Table Name:                   ___________________________________
Policy Field Name:            ___________________________________

OAuth Client ID:              ___________________________________
OAuth Client Secret:          ___________________________________

Anthropic API Key:            ___________________________________
Anthropic Vault ID:           ___________________________________

Temporal Gateway URL (local):  http://localhost:8000
Temporal Gateway URL (public): ___________________________________
```

---

## Where these appear in the code

| File | Variables | Format |
|---|---|---|
| `temporal/gateway.py` | `TEMPORAL_SERVER_ADDRESS`, `TEMPORAL_NAMESPACE`, `TASK_QUEUE_NAME` | Hard-coded defaults |
| `servicenow/ui_action_check_temporal_status.js` | `x_temporal.gateway_url` (system property), `YOUR_TABLE_NAME`, `YOUR_POLICY_FIELD` | Read from system property; field names must match |
| `servicenow/business_rule_resolve_nigo.js` | `x_temporal.gateway_url` (system property) | Read from system property |
| `03_claude-setup/mint-token.sh` | `YOUR_INSTANCE_URL`, `YOUR_CLIENT_ID`, `YOUR_CLIENT_SECRET` | Bash variables (shell script) |
| `03_claude-setup/rotate-vault.js` | `x_snc_insuranct8ex.claude_api_key` (system property), `YOUR_VAULT_ID`, `YOUR_MCP_SERVER_URL` | ServiceNow script; some values read from system properties |
| `claude_desktop_config.json` | `SERVICENOW_INSTANCE_URL`, `SERVICENOW_CLIENT_ID`, `SERVICENOW_CLIENT_SECRET`, `YOUR_VAULT_ID` | JSON config; environment variables for MCP server |

---

## Tips for keeping track

1. **Use a notes file** — Copy the checklist above into a local text file and fill it in as you discover each value
2. **Don't commit secrets** — If you version control this kit, add `*.local`, `.env`, and `claude_desktop_config.json` to `.gitignore` before you start
3. **One variable at a time** — When a setup step asks for a variable, stop and find it before continuing
4. **Double-check special characters** — OAuth secrets often have `$`, `&`, `*`, `'`, etc. — use single quotes in shell scripts to protect them

---

**Still unsure about a variable?** Search `SETUP_GUIDE.md` for the phase where that variable first appears — it should have context for where to find it.
