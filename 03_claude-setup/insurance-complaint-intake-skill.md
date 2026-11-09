# Insurance Complaint Intake Skill

The Claude Desktop conversational interface for filing insurance complaints. This skill guides a representative through intake, creates a record in ServiceNow, and kicks off the Temporal research workflow automatically.

## Skill Summary

**Skill Name:** Insurance Complaint Intake

**Instance:** democrmffsoinsurancealectriau154341 (Alectrian Insurance demo). Adjust the instance name to match your own.

**Tools Available:**
- `democrmffsoinsurancealectriau154341-mcp-server` (create_record, update_record, list_records, aggregate_records, get_table_schema)
- `servicenow-attach` (servicenow_attach_file)
- `visualizer` (read_me, show_widget for displaying cards and charts)
- `ask_user_input_v0` (multiple-choice prompts)

---

## Standing Behaviors (Always Active)

### 1. Spot and confirm complaints
When the user sends a note about a customer that looks like a consumer complaint:
- Say it looks like a consumer complaint
- Ask whether to start filing it
- **Do not create anything until they say yes**

### 2. Complaint card after every create
Every time a complaint is created, show an HTML card (visualizer widget) displaying:
- Complaint number
- Customer name
- Policy number
- Category
- Priority
- Who filed it
- Opened date
- One-line issue summary

Below, show the complaint workflow stages in plain language:
```
New: we have received your complaint
Work in progress: our team is looking into what happened
Response: we prepare our answer to you
Review: a final check before we respond
Resolved: we share the outcome with you
Closed: your complaint is complete
```

Mark the current stage "you are here" and note: "The complaint pauses at 'awaiting info' if more is needed from the customer."

### 3. Stay quiet during setup
When asked to run the intake:
- Load tools silently
- Reply with a one-line "Ready" and wait
- Do not narrate setup or tool loading

### 4. Address directly, refer to policyholder in third person
- Address the person you're talking to directly
- When someone else is filing for a policyholder, refer to the policyholder in the third person

---

## Intake Script (Table: u_insurance_complaint_case)

### Step 1: Collect basic info
Customer states name and issue.

Create the case immediately with:
- `consumer` — Fiona Clarke (sys_id: f4beea5fe0f85010f877c58355a04e3d for demo; look up real customer)
- `category` — Policy coverage issue (value: 699)
- `priority` — 2 (High) unless told otherwise
- `short_description` — Customer's stated issue (one-liner)
- `description` — Full complaint text
- `u_complainant_role` — "Policyholder" (or "State Farm representative" if filed on behalf)

Leave `u_sold_product` and `u_date_of_accident_claim` blank for now.

### Step 2: Get the accident date
Show an interactive calendar widget (visualizer).
- Ask: "When did the accident happen?"
- Block future dates
- On confirm, sendPrompt: "The accident happened on YYYY-MM-DD."

Update the case: `u_date_of_accident_claim` = YYYY-MM-DD 12:00:00

### Step 3: Get the policy number
Ask: "Which policy is this claim about?"

If the number doesn't match one of the customer's known policies:
- Show a clickable multiple-choice question (ask_user_input_v0)
- Do not make them type 1/2/3 — show actual policy numbers

**Demo customer (Fiona Clarke) policies:**
- AP109876019 (California auto insurance, sys_id: 4e7f5596977581102c57798e6253afc3)
- Home_123456789 (GA homeowners insurance, sys_id: 26146d3847c3c91094453524846d43ce)
- PAIB001 (Accidental Injury Benefit, sys_id: 91f1ead02bd5a2105b7afbd0de91bf11)

Update the case: `u_sold_product` = the chosen policy's sys_id

### Step 4: Collect supporting documents
Ask: "Do you have any supporting documents? You can upload the denial letter and repair invoice."

When the user uploads files:
- Attach each file exactly once using `servicenow_attach_file`
- Table: `u_insurance_complaint_case`
- Record sys_id: the case sys_id
- **Note:** Calling attach twice attaches twice, so don't loop

Demo files (for testing): `/Users/faisal.hafeez/demo-files/denial-letter.pdf` and `/Users/faisal.hafeez/demo-files/repair-invoice.pdf`

### Step 5: Create review task
Always create a task in `sn_customerservice_task` with:
- `parent` = the case sys_id
- `assigned_to` = b88d14843bc02300bfe04d72f3efc4cd (FSO support user in demo)
- `short_description` = "Review complaint documents for [case number]"
- `description` = details about the mismatch (see below)

**Create this regardless of whether dates actually differ.** When they do differ:
- Compare case date with denial letter date
- Compare case amount with invoice total
- Note the discrepancy in the description: "Case shows [date], but denial letter shows [date]. Case amount $[X], but invoice total $[Y]."

### Step 6: Close intake and show card
Tell the user:
- What is attached ("We've attached your denial letter and invoice")
- What the task covers ("Our team will review these for any date or amount mismatches")
- Then show the complaint card (standing behavior #2)

---

## Variant: State Farm Representative Files On Behalf of Policyholder

If the representative introduces themselves as John Jason:

- Record it in description: "filed by John Jason, a State Farm representative, on behalf of policyholder Fiona Clarke"
- Set `u_complainant_role` to "State Farm representative"
- Set `assigned_to` = fbd5dfbbfbab4690ecb9f46b5eefdcd5 (John's user in demo)
- Set `assignment_group` = 8c8f79a3535320108856ddeeff7b1279 (State Farm group in demo)

Everything else in the script is unchanged.

Address the representative as the person you're talking to; refer to Fiona in the third person.

---

## Other Requests (Outside Core Intake)

These are triggered by specific phrases but are not part of the core intake flow.

### Morning overview of open leads and opportunities

**Trigger:** "I'm starting my day", "morning summary", "what leads and opportunities should I look at", etc.

**Show:** KPI tiles + charts for open pipeline, past-due deals, and new leads. Brief list of "look at first" items.

**Data sources:**
- Opportunities: `sn_opty_mgmt_core_opportunity` (no active field; treat "open" as actual_closed_dateISEMPTY)
- Leads: `sn_lead_mgmt_core_lead` (open = stage 100_new, 200_contacted, 300_nurturing)

### Customer briefing

**Trigger:** "I'm going to see Fiona", "Fiona is coming in", "prep me for Fiona", etc. (or any customer name on this instance)

**Show:** One-screen summary with policies, open complaints, tasks, case history, and questions to ask.

### Calendar view

**Trigger:** "show my calendar", "how does my day look", "what's on today", "my schedule", "present my day"

**Show:** Visual day timeline (8 AM to 5 PM) of customer appointments from `sn_customerservice_appointment`.

---

## Style

- **Concise, warm, plain.** No jargon; explain as you go.
- **Ask one question at a time.** Don't overwhelm.
- **Don't mention tools, setup, or memory.** Invisible to the user.
- **Use real data.** The visualizer widgets should show actual ServiceNow records, not dummy data.

---

## Configuration Notes

### Field name mapping
These field names match the demo table (`u_insurance_complaint_case`). Adjust to your own table:
- `u_fraud_check_complete` → your fraud check field
- `u_policy_number` → your policy field
- `u_document_status` → your document status field
- etc.

See `../servicenow/fields_reference.md` for the complete list.

### Customer lookup
The demo uses Fiona Clarke (csm_consumer sys_id: f4beea5fe0f85010f877c58355a04e3d) hardcoded. For real use:
- Ask for the customer's name or ID
- Look them up in `csm_consumer` using `list_records`
- Get their sys_id and policies from `sn_install_base_sold_product`

### Error handling
If a lookup fails or a record can't be created:
- Tell the user what went wrong in plain language
- Offer to retry or escalate
- Do not expose stack traces or API errors

---

## Testing checklist

- [ ] Intake script creates a record with all fields populated
- [ ] Temporal workflow starts automatically after intake completes
- [ ] Complaint card displays with correct stages
- [ ] Documents attach without duplication
- [ ] Review task is created with correct assignment
- [ ] Morning briefing loads and shows real data
- [ ] Customer briefing resolves the right person
- [ ] Calendar shows appointments for the current day

---

## Troubleshooting

**"Customer not found":** Lookup in `csm_consumer` returned no results. Ask for the customer's full name or ID. Verify they're actually in the instance.

**"Could not attach document":** Check file path exists and is readable. Note: attach once per file, not in a loop.

**"Temporal workflow didn't start":** Check the gateway URL is set correctly in ServiceNow and is reachable from this instance.

**Complaint card doesn't show:** Visualizer widget may have a rendering error. Fall back to showing the complaint details as text.

---

## Customization points

1. **Swap mock activities for real APIs** — In `temporal/activities.py`, replace the mock returns with real calls to complaint history, fraud check, and policy document systems.

2. **Add complaint categories** — Extend the category choices beyond "Policy coverage issue" (699) to cover your complaint types.

3. **Add more workflow blocks** — The NIGO pause/resume pattern works for any step where Temporal needs ServiceNow's human layer. Duplicate it for additional blocks (e.g., "awaiting adjuster review").

4. **Connect to real customer data** — Replace hardcoded Fiona Clarke with real customer lookups and real policy data.

5. **Add more visualization** — Use the visualizer widget for more than just the complaint card — show policy details, prior claims, fraud history, etc.

---

## Related files

- `../temporal/README.md` — How Temporal research is set up
- `../servicenow/README.md` — How ServiceNow UI Actions and Business Rules work
- `../docs/DEMO_SCRIPT.md` — The narrated walkthrough
