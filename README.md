# FSO + Temporal + ServiceNow + Claude — Complete Insurance Complaint Kit

An end-to-end, working demonstration of how Claude Desktop, ServiceNow, and Temporal work together to handle insurance complaints: **Claude as the conversational front-end intake**, **ServiceNow as the case management and human orchestration layer**, and **Temporal as the durable, long-running Research engine**.

## What you get

A complete, downloadable, reproducible setup that guides you through:

1. **Temporal instance** — The complaint Research workflow, running locally or in the cloud
2. **ServiceNow backend** — Case table, UI Actions, Business Rules, and fields
3. **Claude Desktop front-end** — The insurance-complaint-intake skill with MCP authentication
4. **End-to-end integration** — How they all talk to each other

By the end, you'll have:
- A Temporal workflow that handles complaint research durably (pulling history, fraud checks, documents)
- A ServiceNow case record that reflects that workflow's progress
- A NIGO (missing document) that Temporal can't solve alone, resolved by ServiceNow's human/task layer
- A Claude Desktop interface where a customer service representative can intake a complaint conversationally, and the entire pipeline runs

## Who this is for

- **Solution Architects & Demo Builders** — End-to-end story showing durable workflows + case management + AI front-end
- **Developers** — Code you can fork and modify, with clear extension points
- **Insurance companies** — A concrete pattern for complaint workflows that handle long-running, multi-system research

## Structure

```
├── README.md                          # This file
├── SETUP_GUIDE.md                     # Step-by-step walkthrough (start here)
├── docs/
│   ├── VARIABLES.md                   # All placeholders explained
│   ├── ARCHITECTURE.md                # Design rationale
│   ├── TROUBLESHOOTING.md             # Known issues and fixes
│   └── DEMO_SCRIPT.md                 # Narrated click-through
├── temporal/                          # Temporal workflow + gateway
│   ├── README.md                      # Temporal setup (step 1)
│   ├── requirements.txt
│   ├── workflow.py
│   ├── activities.py
│   ├── worker.py
│   ├── gateway.py
│   └── starter_client.py
├── servicenow/                        # ServiceNow backend
│   ├── README.md                      # ServiceNow setup (step 2)
│   ├── fields_reference.md
│   ├── ui_action_check_temporal_status.js
│   └── business_rule_resolve_nigo.js
└── 03_claude-setup/                   # Claude Desktop front-end
    ├── README.md                      # Claude setup (step 3)
    ├── insurance-complaint-intake-skill.md
    ├── mint-token.sh
    └── rotate-vault.js
```

## Quick start

1. **Read `SETUP_GUIDE.md`** — It walks you through each phase, step by step
2. **Follow `temporal/README.md`** — Get the Temporal instance running
3. **Follow `servicenow/README.md`** — Configure the ServiceNow backend
4. **Follow `03_claude-setup/README.md`** — Set up Claude Desktop with MCP
5. **Run the demo** — Follow `docs/DEMO_SCRIPT.md`

If anything doesn't match what's expected, check `docs/TROUBLESHOOTING.md` — most issues have already been hit and fixed.

## What this is NOT

- Not a production-ready integration — the Temporal activities return mock data; you'll swap them for real API calls
- Not a one-click installer — ServiceNow config requires a human admin following the steps
- Not a template for a different complaint type — field names, table structure, and workflow stages are specific to insurance, but the pattern generalizes to any long-running, multi-system case workflow

## The key insight

This demo's most important piece isn't that Temporal, ServiceNow, and Claude each work — it's that **Temporal gets stuck mid-workflow and ServiceNow's human/task layer gets it unstuck**. That's the reverse of most "A and B work together" demos, and it's the most concrete argument for why they belong in the same system.

See `docs/ARCHITECTURE.md` for the full story.

## Quick reference: all variables you'll need to customize

See `docs/VARIABLES.md` for complete definitions. At a glance:

| Variable | Example | Where you get it |
|---|---|---|
| `YOUR_INSTANCE_URL` | `https://democrmffsoinsurancealectriau154341.service-now.com` | Your ServiceNow instance |
| `YOUR_INSTANCE_NAME` | `democrmffsoinsurancealectriau154341` | From the URL |
| `YOUR_CLIENT_ID` | `a1c7b931e2bd4342a372b54bb3b9e131` | ServiceNow Machine Identity Console |
| `YOUR_CLIENT_SECRET` | `T*1(d:RLkq)9*n0;F'...` | ServiceNow Machine Identity Console |
| `YOUR_ANTHROPIC_API_KEY` | `sk-ant-v0-...` | Anthropic console |
| `YOUR_VAULT_ID` | `vlt_011Cg4neN4eg3tLt7GPs4bDp` | Anthropic console |
| `YOUR_TABLE_NAME` | `u_insurance_complaint_case` | Your ServiceNow table |
| `YOUR_POLICY_FIELD` | `u_policy_number` | Your ServiceNow table |

---

**Ready?** Start with `SETUP_GUIDE.md`.
