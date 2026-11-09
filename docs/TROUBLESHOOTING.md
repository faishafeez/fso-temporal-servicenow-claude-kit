# Troubleshooting

Every one of these was hit and resolved while building this demo — not
hypothetical.

## "command not found: brew" / Homebrew install fails with a permissions error

Common on corporate-managed Macs where the account isn't a local
Administrator. Skip Homebrew entirely — download the Temporal CLI binary
directly to `~/bin` instead (see `../temporal/README.md` step 1). No admin
rights required for that path.

## `TypeError: unsupported operand type(s) for |: 'type' and 'NoneType'`

Python 3.9 doesn't support the `X | None` type-hint syntax used in newer
Python. Fix: `from __future__ import annotations` as the first import in
the affected file — this makes all type hints lazy strings, never
evaluated at runtime, regardless of Python version. Already present in
`workflow.py` and `gateway.py` in this kit — if you see this error, it
means a file got reverted or re-created without that line.

## A large multi-line paste into Terminal silently drops lines or characters

Terminal paste of big blocks (heredocs, long base64 strings) is not fully
reliable — this caused real, confusing failures during development
(lines dropped from the middle of a heredoc; a base64 string truncated
mid-transfer). **Don't replace a whole file via a big paste.** Instead,
make small, targeted changes with a short Python script that does an exact
find-and-replace on a unique anchor string, e.g.:

```
python3 - << 'PYEOF'
with open('workflow.py') as f:
    content = f.read()
old = '''...exact existing text...'''
new = '''...replacement text...'''
assert content.count(old) == 1, "anchor not found"
content = content.replace(old, new, 1)
with open('workflow.py', 'w') as f:
    f.write(content)
print("SUCCESS")
PYEOF
```

Verify the anchor text with `cat -n <file>` first if you're not 100% sure
it matches exactly (whitespace included) — an `AssertionError` means the
file's real content doesn't match what you assumed, which is useful
information, not a dead end.

## ngrok's TLS handshake fails immediately (`SSL_ERROR_SYSCALL`), but other HTTPS sites work fine

This is a network blocking ngrok specifically by its domain (visible even
inside the encrypted handshake via SNI) — confirmed on both a corporate
network and, separately, a hotel guest network. It is not a bug in this
code. Workarounds:
- Tether to a phone hotspot and retry
- Ask IT to allowlist the tunnel domain for a sanctioned use case
- Best long-term fix: run the Temporal server/worker/gateway on a small
  cloud VM with its own public IP instead of tunneling from a laptop —
  removes the dependency on whatever network you happen to be on

Test with `curl -v https://your-tunnel-url/health` — if the TCP connection
succeeds but the TLS handshake dies instantly, that's this exact issue.

## Lost track of which terminal is running what

```
lsof -i :8000              # finds whatever process is using the gateway's port
ps aux | grep worker.py    # finds the worker process
```
Either gives you a PID you can `kill`, then restart cleanly in whichever
terminal tab you're currently in, rather than hunting through tabs.

## A workflow "isn't found" when you try to check its status or signal it

The in-memory Temporal dev server loses all workflow state if it's
restarted — this is expected behavior for `start-dev`, not a bug. Every
workflow needs to be started again after any restart of Terminal 1.

Also double check the ID actually matches: the gateway always builds the
Temporal workflow ID as `complaint-{complaint_id}` — if ServiceNow's
record number and the ID used to start the workflow don't match exactly,
you'll get a "not found" even though a workflow is genuinely running
under a different ID.

## A new ServiceNow UI Action doesn't show up on the form

If you're using Configurable Workspace (CWF) rather than the classic UI:
check the `...` overflow menu (UI Actions that don't fit the primary
button row land there automatically), and do a hard refresh of the tab —
Workspace caches UI Action metadata client-side and often doesn't pick up
a new or changed action without one. If it's still missing after that,
check the UI Action's `Order` field, and whether the record page (in UI
Builder) is configured with a curated action list rather than "show all
eligible UI actions."

## Clicking "Check Temporal Status" twice after a NIGO task already exists creates a second task

Known limitation in this demo's UI Action — there's no guard field
checking whether a task was already created for this NIGO. Harmless for a
demo (just don't double-click after the first task appears); add a
boolean "task already created" field and check it in the script if you
want this to be safe for repeated/production use.
