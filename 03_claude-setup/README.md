# Claude Desktop Setup — MCP Authentication & Front-End Skill

This phase sets up Claude Desktop to be the conversational intake interface for complaint filing.

**Prerequisite:** Phases 1 and 2 (Temporal and ServiceNow) must be complete before starting this.

**Estimated time:** 10–15 minutes

---

## What you're setting up

1. **OAuth token minting** — Generate short-lived JWT tokens from your ServiceNow OAuth client
2. **Anthropic vault credential rotation** — Store tokens in Anthropic's vault, refresh them periodically
3. **MCP authentication** — Claude Desktop can now call ServiceNow to create records
4. **Insurance complaint intake skill** — The conversational interface itself

---

## 1. Get your OAuth credentials

You'll need the Client ID and Secret from your ServiceNow OAuth client (created during Phase 2).

**If you don't have them:**
- ServiceNow → Machine Identity Console
- OAuth Integrations → Inbound
- Find the integration you created (or create a new one):
  - Grant type: Client Credentials
  - Token Format: **JWT** (not opaque — this is critical)
  - Scope restriction: Broadly scoped (NOT "Allow access only to APIs in selected scope")
  - Assigned user: admin (for demo; restrict to actual service account for production)
- Copy the **Client ID** and **Client Secret**

Store these securely — you'll use them in the next step.

---

## 2. Get your Anthropic credentials

**Anthropic API Key:**
- Go to https://console.anthropic.com → API Keys
- Create or copy an existing API key
- Keep this secret

**Anthropic Vault ID:**
- Go to https://console.anthropic.com → Vaults
- Create a new vault or identify an existing one
- Copy the Vault ID (format: `vlt_...`)

---

## 3. Set up the token minting script

This script generates a fresh JWT token from ServiceNow's OAuth endpoint. You'll run it whenever you need a new token (or before it expires).

**Copy `mint-token.sh` from this folder** and customize it:

```bash
# Edit these three lines:
INSTANCE_URL="https://YOUR_INSTANCE_NAME.service-now.com"
CLIENT_ID="YOUR_CLIENT_ID"
CLIENT_SECRET='YOUR_CLIENT_SECRET'   # single quotes protect $ and special chars
```

**Test it:**
```bash
bash mint-token.sh
```

**Expected output:**
```json
{
  "access_token": "eyJraWQiOi...",  # very long JWT string
  "expires_in": 31535999,            # token lifespan in seconds
  "token_type": "Bearer"
}
Token segments: 3 (need 3 for JWT)
```

**If you see `Token segments: 1`:**
- Your OAuth client's Token Format is set to "opaque" instead of JWT
- Go back to ServiceNow Machine Identity Console and change it to JWT
- Try again

**Save the `access_token` value** — you'll need it in the next step.

---

## 4. Rotate the vault credential

This script stores your token in Anthropic's vault and configures it to authenticate Claude Desktop to ServiceNow.

**Copy `rotate-vault.js` from this folder** and customize it:

```javascript
var apiKey = gs.getProperty('x_snc_insuranct8ex.claude_api_key');  // Keep as-is
var vaultId = 'vlt_011Cg4neN4eg3tLt7GPs4bDp';        // Replace with YOUR_VAULT_ID
var oldCredentialId = '';                             // Leave blank on first run
var mcpServerUrl = 'https://YOUR_INSTANCE_NAME.service-now.com/sncapps/mcp-server/mcp/sn_mcp_server_default';
var newToken = 'eyJraWQiOi...';                       // Paste the access_token from step 3
```

**Run this script in ServiceNow:**
- ServiceNow → System Applications → Scripts - Background
- Paste the entire rotate-vault.js into the Script field
- Click Execute

**Expected output in the logs:**
```
VAULT_CRED_DELETE_STATUS: 200 (or 404 if this is the first run)
VAULT_CRED_CREATE_STATUS: 200
VAULT_CRED_CREATE_BODY: {"id":"vcrd_018gaak3eCWLHwQxpWnMepES",...}
```

**Save the credential ID** (the `id` field from CREATE_BODY) — you'll need it next time you rotate.

---

## 5. Configure Claude Desktop MCP

Claude Desktop connects to ServiceNow via MCP (Model Context Protocol).

**Edit your Claude Desktop config:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

**Find or create the `mcpServers` section** and add:

```json
"servicenow-mcp": {
  "command": "/Users/YOUR_USERNAME/.local/bin/uvx",
  "args": ["mcp-server-servicenow"],
  "env": {
    "PATH": "/Users/YOUR_USERNAME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin",
    "SERVICENOW_INSTANCE_URL": "https://YOUR_INSTANCE_NAME.service-now.com",
    "SERVICENOW_AUTH_TYPE": "oauth",
    "SERVICENOW_CLIENT_ID": "YOUR_CLIENT_ID",
    "SERVICENOW_CLIENT_SECRET": "YOUR_CLIENT_SECRET",
    "SERVICENOW_VAULT_ID": "vlt_YOUR_VAULT_ID",
    "SERVICENOW_CREDENTIAL_ID": "vcrd_018gaak3eCWLHwQxpWnMepES"
  }
}
```

**Replace:**
- `YOUR_USERNAME` — your macOS/Linux username
- `YOUR_INSTANCE_NAME` — your ServiceNow instance name
- `YOUR_CLIENT_ID` — from step 1
- `YOUR_CLIENT_SECRET` — from step 1
- `vlt_YOUR_VAULT_ID` — from step 2
- `vcrd_...` — the credential ID from step 4

**Save and restart Claude Desktop.**

---

## 6. Test the connection

In Claude Desktop, open a new chat and ask:

```
Get me the list of users in my ServiceNow instance.
```

If it works, you'll see a list of users. If it fails, check:
- Is the MCP server config correct?
- Have you restarted Claude Desktop?
- Does the credential ID in the config match the one from step 4?

---

## 7. Load the insurance-complaint-intake skill

The skill definition is in `insurance-complaint-intake-skill.md`.

**In Claude Desktop:**
1. Create a new chat
2. Say: `I'm starting my day` or `I'm going to see Fiona`
3. The skill should auto-trigger and show you your calendar/briefing

If the skill doesn't trigger:
- Make sure you have MCP access (step 6 test should pass)
- Make sure the skill is loaded in your Claude Code settings
- Restart Claude Desktop

---

## Refreshing the token

Tokens expire. When yours is about to expire (or after 30 days, or on demand):

1. Run `bash mint-token.sh` again
2. Copy the new `access_token`
3. Update `rotate-vault.js` with the new token and the **old credential ID** (from the previous rotation)
4. Run it in ServiceNow Scripts - Background
5. Update Claude Desktop's config with the new credential ID

The second and subsequent times are faster because the old credential is deleted first.

---

## Troubleshooting

**"Could not reach ServiceNow" error in Claude Desktop:**
- Is the instance URL correct and reachable? (Test in browser)
- Are the Client ID and Secret correct?
- Is the MCP server configured with the right environment variables?

**MCP server won't start:**
- Run `which uvx` — if not found, install it: `pip install uv`
- Run `uvx --help` to confirm it works
- Check the `PATH` in the MCP config is correct for your machine

**Token has 1 segment instead of 3:**
- Your OAuth client's Token Format is set to "opaque"
- Change it to JWT in ServiceNow Machine Identity Console

**Claude Desktop doesn't show the skill:**
- Check that the MCP server is working (test in step 6)
- Hard restart Claude Desktop
- Check `docs/TROUBLESHOOTING.md` for Workspace visibility issues

---

## Next: Try the end-to-end flow

Once this phase is complete and the skill loads:
- Use Claude Desktop to file a complaint (conversationally)
- Watch it create a record in ServiceNow
- Click "Check Temporal Status" on that record
- Follow `docs/DEMO_SCRIPT.md` for the full walkthrough

**All three phases working together** is when this truly shines — that's your proof that Claude, ServiceNow, and Temporal all belong in the same system.
