#!/usr/bin/env bash
# Mint a ServiceNow OAuth client_credentials bearer token (Mac / Linux).
#
# This script generates a fresh JWT token from your ServiceNow OAuth client.
# Use it whenever you need a new token for Anthropic vault credential rotation.
#
# BEFORE RUNNING: fill in YOUR_INSTANCE_NAME, YOUR_CLIENT_ID, and YOUR_CLIENT_SECRET below.
#
# NOTE ON PLATFORM COVERAGE: this build was tested on macOS. It should work
# unchanged on Linux (both ship a real `curl`, no alias problems). If you're
# on Windows, use the PowerShell equivalent (mint-token.ps1) or run this under WSL.
#
# *** THE #2 GOTCHA OF THIS ENTIRE BUILD, AFTER SCOPE FENCING ***
# The MCP Server's inbound auth validator REQUIRES a JWT-format token
# (3 dot-separated segments: header.payload.signature). A perfectly valid
# OAuth token can still be OPAQUE (a single random-looking string, zero
# dots) if the OAuth client's "Token Format" is not explicitly set to JWT.
# An opaque token gets this exact rejection when the MCP server tries to
# use it:
#   {"error":"Authentication failed","message":"Token validation failed: Not enough segments","details":"Please provide a valid JWT token"}
# This is NOT a credentials problem — the client_id/secret can be 100%
# correct and you'll still get this. Before debugging anything else about a
# rejected token, count the dots. Zero or one dot = wrong token format at
# the OAuth client level, not a bad secret.
#
# BEFORE RUNNING IN SERVICENOW: in Machine Identity Console (not the classic
# Application Registry wizard), create an inbound OAuth integration with:
#   - Grant type: Client Credentials
#   - Token Format: JWT          <-- the field everyone misses
#   - Scope restriction: Broadly scoped (NOT "Allow access only to APIs in
#     selected scope" -- checking that box means MCP clients can't fetch
#     tools from the server at all)
#   - OAuth Application User set to an account with the roles Claude's
#     writes will need (admin for a demo/sandbox instance is simplest)
# Then fill in the values below from that record.

INSTANCE_URL="https://YOUR_INSTANCE_NAME.service-now.com"
CLIENT_ID="YOUR_CLIENT_ID"
CLIENT_SECRET='YOUR_CLIENT_SECRET'   # single quotes protect $ and backticks in the secret

RESPONSE=$(curl -sS "$INSTANCE_URL/oauth_token.do" \
    -d grant_type=client_credentials \
    -d client_id="$CLIENT_ID" \
    -d client_secret="$CLIENT_SECRET")

echo "$RESPONSE"

# Quick sanity check: does the access_token have 2 dots in it (3 segments)?
# If this doesn't print "3", stop here and fix Token Format on the OAuth
# client before doing anything else -- pushing an opaque token into the
# vault credential will just reproduce the same rejection downstream.
if command -v jq >/dev/null 2>&1; then
    TOKEN=$(echo "$RESPONSE" | jq -r '.access_token')
    SEGMENTS=$(echo "$TOKEN" | awk -F'.' '{print NF}')
    echo "Token segments: $SEGMENTS (need 3 for JWT)"
else
    echo "(install jq for an automatic segment count, or eyeball the access_token above for 2 dots)"
fi
