# Complete Setup Guide — FSO + Temporal + ServiceNow + Claude

Follow this guide in order. Each phase should be completed before moving to the next one.

**Estimated time:** 45–60 minutes total (depending on how long ServiceNow admin access takes to get).

---

## Phase 1: Temporal Instance (15–20 minutes)

The durable workflow engine that handles complaint research.

**Start here:** [`temporal/README.md`](temporal/README.md)

Follow it **step by step**, confirming each command's output before moving to the next. Don't skip ahead or batch commands together — several steps depend on prior processes staying alive in background terminals.

**What you'll have when done:**
- Temporal CLI installed
- Local Temporal server running (`temporal server start-dev`)
- Python worker executing the workflow
- REST gateway listening on `http://localhost:8000`
- Test: `curl http://localhost:8000/health` returns `{"status":"ok"}`

**If anything doesn't work:** Check `docs/TROUBLESHOOTING.md` first — most issues have known fixes.

---

## Phase 2: ServiceNow Backend (20–25 minutes)

The case management and human orchestration layer.

**Start here:** [`servicenow/README.md`](servicenow/README.md)

You'll need **admin access** to a ServiceNow instance. This phase involves:

1. Creating fields on your complaint/case table (see [`servicenow/fields_reference.md`](servicenow/fields_reference.md))
2. Creating a system property with your Temporal gateway's URL
3. Creating a UI Action (button) on the form
4. Creating a Business Rule that signals Temporal when a NIGO is resolved

**Before you start:** Know your instance URL and table name. See `docs/VARIABLES.md` if unsure what goes where.

**Network note:** If your Temporal gateway is running on your laptop, you'll need a tunnel (ngrok) so ServiceNow can reach it. See `temporal/README.md` for details.

**What you'll have when done:**
- Fields added to your complaint table
- "Check Temporal Status" button on the form
- Business rule that signals Temporal on document resolution
- Test: Click the button on a fresh record — it should auto-start a workflow

---

## Phase 3: Claude Desktop Front-End (10–15 minutes)

The conversational intake interface.

**Start here:** [`03_claude-setup/README.md`](03_claude-setup/README.md)

This phase sets up:

1. OAuth token minting from ServiceNow
2. Anthropic vault credential rotation
3. The insurance-complaint-intake skill in Claude Desktop
4. MCP authentication so Claude can call ServiceNow

**Prerequisites:**
- Anthropic API key (from https://console.anthropic.com)
- ServiceNow OAuth client (created during Phase 2)

**What you'll have when done:**
- `mint-token.sh` configured and tested
- `rotate-vault.js` rotated with a year-long token
- Claude Desktop skill ready to take complaints conversationally
- Test: Open Claude Desktop, start a new chat, say "I'm starting my day" — should see your calendar and briefing

---

## Phase 4: End-to-End Test (10 minutes)

Run the complete flow.

**Follow:** `docs/DEMO_SCRIPT.md`

1. Open Claude Desktop and use the insurance-complaint-intake skill to file a complaint
2. Watch it create a record in ServiceNow
3. Open that record and click "Check Temporal Status"
4. Watch Temporal research the complaint, hit the NIGO, and pause
5. Mark the document reviewed in ServiceNow
6. Watch Temporal resume and complete

**What to look for:**
- Fields populate as Temporal reports progress
- A task is created when the NIGO is hit
- Workflow completes after resolving the NIGO
- Web UI shows it all in `http://localhost:8233`

---

## Troubleshooting quick reference

**Something doesn't match what the guide says:**
- Check `docs/TROUBLESHOOTING.md` — most issues have known fixes
- Check `docs/VARIABLES.md` — make sure you substituted the right values

**A process stopped working after Phase X:**
- Processes from earlier phases are still running (Temporal server, worker, gateway)
- Terminal tabs get lost — use `lsof -i :8000` to find them

**ServiceNow button doesn't show up:**
- Hard refresh the tab (Cmd+Shift+R or Ctrl+Shift+R)
- Check the `...` overflow menu for the button
- Check `docs/TROUBLESHOOTING.md` for Workspace-specific issues

**Temporal workflow doesn't start:**
- Check the gateway URL is reachable: `curl <YOUR_GATEWAY_URL>/health`
- Check the system property `x_temporal.gateway_url` is set correctly
- Check the worker is still running

---

## What to customize for your own instance

See `docs/VARIABLES.md` for the complete list. Main ones:

- **Complaint table name** — `u_insurance_complaint_case` → your table
- **Field names** — `u_fraud_check_complete`, `u_policy_number`, etc. → your fields
- **Instance URL** — `https://democrmffsoinsurancealectriau154341.service-now.com` → your instance
- **Gateway URL** — Where Temporal is running (localhost for dev, ngrok/public IP for ServiceNow to reach)
- **OAuth credentials** — Client ID and Secret from your ServiceNow Machine Identity Console

---

## Next steps after setup

1. **Swap mock data for real APIs** — `temporal/activities.py` has comments showing where to replace the mock return values with real HTTP calls (complaint history, fraud checks, policy documents)
2. **Add more workflow stages** — The NIGO pause/resume pattern works for any blocking step; duplicate it for other places where Temporal needs ServiceNow's human layer
3. **Connect to your real data sources** — Update activities to call your actual complaint history, SIU, and document store systems
4. **Run it against real customer records** — This demo uses Fiona Clarke's test ID; point it at your own customer table

---

**Still stuck?** Open `docs/TROUBLESHOOTING.md` and search for your issue. If it's not there, file an issue with details about where the guide's output diverged from what's described.
