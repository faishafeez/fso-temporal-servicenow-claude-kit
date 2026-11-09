"""
The REST gateway ServiceNow talks to.

Temporal's own protocol is gRPC, which ServiceNow's Integration Hub REST
step (or a classic REST Message) can't call directly — so this small
FastAPI app sits in between: plain REST in from ServiceNow, Temporal
client calls out to the workflow.

Run it with:

    uvicorn gateway:app --reload --port 8000

Endpoints:

  POST /complaints/{complaint_id}/start-research
      Body: {"complaint_id": "...", "policy_number": "..."}
      Call this from ServiceNow right after Triage/intake completes —
      or let the ServiceNow UI Action auto-start it on first check
      (see servicenow/ui_action_check_temporal_status.js).

  GET /complaints/{complaint_id}/status
      The one call ServiceNow needs for its "Check Temporal Status" step.
      Response shape:
        {
          "complaint_id": "CMP0001",
          "found": true,
          "complaint_history_done": true,
          "fraud_check_done": true,
          "fraud_risk_score": "low",
          "document_review_complete": false,
          "document_status": "NIGO-Missing Documents",
          "nigo_flagged": true,
          "nigo_resolved": false,
          "nigo_reason": "Missing endorsement effective date on policy file"
        }
      If no workflow exists yet for that complaint_id, "found" is false
      and every other field is omitted — that's ServiceNow's cue to call
      start-research instead.

  POST /complaints/{complaint_id}/resolve-nigo
      Body: {"endorsement_date": "2025-01-01"}
      Call this once the missing document has actually been resolved on
      the ServiceNow side (e.g. a Business Rule firing when a status
      field flips to "IGO").

  GET /complaints/{complaint_id}/result
      Returns the final workflow result once everything (including any
      NIGO) has resolved and the payment step has run.
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from temporalio.client import Client

from workflow import ComplaintResearchWorkflow, ComplaintInput, NigoResolution

app = FastAPI(title="Temporal-ServiceNow Gateway")

_client: Client | None = None


async def get_client() -> Client:
    global _client
    if _client is None:
        _client = await Client.connect("localhost:7233", namespace="default")
    return _client


def workflow_id_for(complaint_id: str) -> str:
    return f"complaint-{complaint_id}"


class StartResearchRequest(BaseModel):
    complaint_id: str
    policy_number: str


class ResolveNigoRequest(BaseModel):
    endorsement_date: str


@app.post("/complaints/{complaint_id}/start-research")
async def start_research(complaint_id: str, body: StartResearchRequest):
    client = await get_client()
    handle = await client.start_workflow(
        ComplaintResearchWorkflow.run,
        ComplaintInput(complaint_id=complaint_id, policy_number=body.policy_number),
        id=workflow_id_for(complaint_id),
        task_queue="complaint-research-task-queue",
    )
    return {"workflow_id": handle.id, "status": "started"}


@app.get("/complaints/{complaint_id}/status")
async def get_status(complaint_id: str):
    client = await get_client()
    handle = client.get_workflow_handle(workflow_id_for(complaint_id))
    try:
        status = await handle.query(ComplaintResearchWorkflow.research_status)
    except Exception as e:
        return {"complaint_id": complaint_id, "found": False, "detail": str(e)}
    return {"complaint_id": complaint_id, "found": True, **status}


@app.post("/complaints/{complaint_id}/resolve-nigo")
async def resolve_nigo(complaint_id: str, body: ResolveNigoRequest):
    client = await get_client()
    handle = client.get_workflow_handle(workflow_id_for(complaint_id))
    await handle.signal(
        ComplaintResearchWorkflow.resolve_nigo,
        NigoResolution(endorsement_date=body.endorsement_date),
    )
    return {"complaint_id": complaint_id, "status": "nigo_resolution_sent"}


@app.get("/complaints/{complaint_id}/result")
async def get_result(complaint_id: str):
    client = await get_client()
    handle = client.get_workflow_handle(workflow_id_for(complaint_id))
    try:
        result = await handle.result()
    except Exception as e:
        return {"complaint_id": complaint_id, "status": "still_running_or_error", "detail": str(e)}
    return {"complaint_id": complaint_id, "status": "completed", "result": result}


@app.get("/health")
async def health():
    return {"status": "ok"}
