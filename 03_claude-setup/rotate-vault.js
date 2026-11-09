// ServiceNow background script -- rotates the Anthropic Vault Credential
// that holds the bearer token the Managed Agent uses to authenticate to
// your Provisioned MCP Server. Run this every time you mint a fresh token
// with mint-token.sh.
//
// Platform note: this script runs server-side inside ServiceNow (Scripts -
// Background), so it is IDENTICAL on Mac and Windows -- there is no
// platform-specific version of this file. It's listed here because it's
// part of the same operational loop as the platform-specific mint_token
// scripts.
//
// WHY A BACKGROUND SCRIPT AND NOT A LOCAL CURL COMMAND:
// gs.getProperty() decrypts a password2-type system property INSIDE a
// server-side script -- this lets the script authenticate to Anthropic's
// API using your stored Anthropic API key without that key ever being
// retrievable in plaintext via the Table API, and without you having to
// paste it into a terminal command on your own machine.
//
// *** GOTCHAS THIS SCRIPT ALREADY WORKS AROUND ***
// 1. A static_bearer Vault Credential is IMMUTABLE once created -- PATCH
//    and PUT both return 405 Method Not Allowed. The only way to change
//    the token value is DELETE the old credential, then POST a new one.
// 2. The create POST body's secret field is named "token", NOT "secret"
//    (guessing "secret" gets a precise 400: Failed to parse request body:
//    unknown field "secret" -- a useful error in that it tells you the
//    schema, unlike the opaque 405 from PATCH/PUT).
// 3. A vault enforces ONE credential per mcp_server_url -- creating a
//    second one for the same URL while the old one still exists 409s with
//    "A credential already exists for this MCP server URL." Delete first.
//
// FIND/REPLACE BEFORE USE: every ALL_CAPS placeholder below.

var apiKey = gs.getProperty('x_snc_insuranct8ex.claude_api_key');
var vaultId = 'YOUR_VAULT_ID';                 // e.g. vlt_xxxxxxxxxxxx
var oldCredentialId = '';                      // e.g. vcrd_xxxxxxxxxxxx -- blank/omit on first run
var mcpServerUrl = 'https://YOUR_INSTANCE_NAME.service-now.com/sncapps/mcp-server/mcp/sn_mcp_server_default';
var newToken = 'PASTE_THE_FRESH_JWT_ACCESS_TOKEN_HERE';

if (oldCredentialId) {
    var del = new sn_ws.RESTMessageV2();
    del.setEndpoint('https://api.anthropic.com/v1/vaults/' + vaultId + '/credentials/' + oldCredentialId);
    del.setHttpMethod('DELETE');
    del.setRequestHeader('anthropic-version', '2023-06-01');
    del.setRequestHeader('anthropic-beta', 'managed-agents-2026-04-01');
    del.setRequestHeader('x-api-key', apiKey);
    var delResp = del.execute();
    gs.info('VAULT_CRED_DELETE_STATUS: ' + delResp.getStatusCode());
    gs.info('VAULT_CRED_DELETE_BODY: ' + delResp.getBody());
}

var create = new sn_ws.RESTMessageV2();
create.setEndpoint('https://api.anthropic.com/v1/vaults/' + vaultId + '/credentials');
create.setHttpMethod('POST');
create.setRequestHeader('content-type', 'application/json');
create.setRequestHeader('anthropic-version', '2023-06-01');
create.setRequestHeader('anthropic-beta', 'managed-agents-2026-04-01');
create.setRequestHeader('x-api-key', apiKey);
create.setRequestBody(JSON.stringify({
    display_name: 'ServiceNow MCP credential',
    auth: {
        type: 'static_bearer',
        mcp_server_url: mcpServerUrl,
        token: newToken   // field name is "token", NOT "secret"
    }
}));
var createResp = create.execute();
gs.info('VAULT_CRED_CREATE_STATUS: ' + createResp.getStatusCode());
gs.info('VAULT_CRED_CREATE_BODY: ' + createResp.getBody());

// Copy the new credential's "id" from the CREATE_BODY log line above into
// your own <scope>.mcp_credential_id system property for your own records
// (nothing at runtime actually reads that property back -- the Managed
// Agent session only needs vault_ids, matched to a credential by
// mcp_server_url internally -- but keeping it current avoids confusion
// later).
//
// After rotating: start a NEW chat session in the embedded panel (not an
// existing one) -- MCP tool availability is negotiated once per session,
// so an already-open session keeps using whatever credential was live
// when IT started.
