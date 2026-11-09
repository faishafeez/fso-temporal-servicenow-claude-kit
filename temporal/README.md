# Temporal setup — Complaint Research demo

This folder is self-contained: everything needed to run a local Temporal
server, a worker, and a REST gateway that simulates the "Research" step of
an insurance complaint — pulling complaint history, running a fraud-signal
check, hitting a NIGO (Not In Good Order — a missing document), and pausing
until told to resume.

**If you're Claude Code reading this to set it up for someone:** work
through the numbered steps below in order, running each command and
confirming its expected output before moving to the next one. Don't skip
ahead or batch multiple steps' commands together — several steps depend on
the previous one's process still being alive in the background. If a
command's output doesn't match what's described, stop and see
`../docs/TROUBLESHOOTING.md` before continuing; don't guess at a fix.

---

## What you end up with

Three long-running processes, each in its own terminal, plus one
command you run to test:

| Terminal | Command | Purpose |
|---|---|---|
| 1 | `temporal server start-dev` | The Temporal service itself + Web UI |
| 2 | `python worker.py` | Executes the workflow/activity code |
| 3 | `uvicorn gateway:app --port 8000` | REST API a system like ServiceNow can call |
| (any) | `python starter_client.py` | Kicks off one test run |

---

## 1. Install the Temporal CLI

**Check what you have first:**
```
temporal --version
```
If that already prints a version number, skip to step 2.

**Mac, with Homebrew available:**
```
brew install temporal
```

**Mac, no admin rights (Homebrew install fails/unavailable), or you'd rather not use Homebrew:**
Download the binary directly — no install, no admin rights needed.

Check your chip first:
```
uname -m
```
`arm64` = Apple Silicon, `x86_64` = Intel.

```
# Apple Silicon:
curl -L 'https://temporal.download/cli/archive/latest?platform=darwin&arch=arm64' -o temporal.tar.gz

# Intel:
curl -L 'https://temporal.download/cli/archive/latest?platform=darwin&arch=amd64' -o temporal.tar.gz
```

Then:
```
tar -xzf temporal.tar.gz
mkdir -p ~/bin
mv temporal ~/bin/
chmod +x ~/bin/temporal
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

If macOS blocks it the first time you run it ("cannot be opened because the
developer cannot be verified" or it just says `Killed`):
```
xattr -d com.apple.quarantine ~/bin/temporal
```

**Linux / Windows:** download the matching binary from
https://github.com/temporalio/cli/releases and put it on your PATH.

**Confirm it worked:**
```
temporal --version
```

## 2. Start the local Temporal server (Terminal 1)

```
temporal server start-dev
```

Leave this running — it'll print server info and then go quiet. That's
correct, not stuck.

Confirm it's really up: open `http://localhost:8233` in a browser. You
should see the Temporal Web UI, empty for now.

## 3. Set up the Python environment

In this folder:
```
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

If your Python is 3.9 specifically: this code already accounts for that
(see `workflow.py` and `gateway.py`'s `from __future__ import annotations`
line) — don't remove those lines, they're load-bearing on 3.9.

## 4. Start the worker (Terminal 2)

Same folder, venv activated:
```
python worker.py
```
Expect: `Worker started. Listening on task queue 'complaint-research-task-queue'...`

Leave this running too.

## 5. Run a test workflow (any terminal, venv activated)

```
python starter_client.py
```

Go watch it in the Web UI (`http://localhost:8233`). You'll see
`pull_complaint_history` and `check_fraud_signals` complete, then
`pull_policy_documents` fail — on purpose — and the workflow will sit
there. That's the NIGO pause. **It's supposed to look stuck.**

## 6. Push it past the NIGO manually, to prove the mechanism works

```
temporal workflow signal \
  --workflow-id complaint-CMP0001 \
  --name resolve_nigo \
  --input '{"endorsement_date": "2025-01-01"}'
```

Watch the Web UI — the workflow should resume immediately, run
`create_partial_payment`, and complete.

**If you got this far and it worked: the Temporal side is fully proven.**

## 7. Start the REST gateway (Terminal 3)

```
uvicorn gateway:app --reload --port 8000
```

Test it:
```
curl localhost:8000/health
# Expect: {"status":"ok"}
```

## 8. Start a workflow matching a real record number

Rather than the fixed `CMP0001`, use whatever ID your target system
actually uses:
```
python start_complaint.py INSCMPL0001035
curl http://localhost:8000/complaints/INSCMPL0001035/status
```

You should get back the full status JSON — see `gateway.py`'s docstring
for the exact shape.

---

## Connecting this to an external system (e.g. ServiceNow)

Whatever calls this gateway needs network access to wherever it's running.
If the gateway is on a laptop rather than a public server, you'll need a
tunnel — `ngrok http 8000` is the fastest option (see
`../docs/TROUBLESHOOTING.md` for a network caveat about this). Point the
external system at the tunnel's public URL instead of `localhost`.

See `../servicenow/README.md` for exactly how this was wired into a
ServiceNow instance, including the scripts used.
