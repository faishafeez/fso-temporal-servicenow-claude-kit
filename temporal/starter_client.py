"""
The simplest possible way to start a workflow run — fixed complaint ID,
no arguments, useful for a first smoke test before anything else (the
gateway, ServiceNow) is involved.

    python starter_client.py

Then open the Temporal Web UI (http://localhost:8233) and watch it run.
It'll pause on the NIGO. To push it past that manually:

    temporal workflow signal \
      --workflow-id complaint-CMP0001 \
      --name resolve_nigo \
      --input '{"endorsement_date": "2025-01-01"}'

For starting a workflow under a specific complaint number (e.g. matching
a real ServiceNow record like INSCMPL0001035), use start_complaint.py
instead — this file always uses "CMP0001".
"""

import asyncio
from temporalio.client import Client

from workflow import ComplaintResearchWorkflow, ComplaintInput


async def main():
    client = await Client.connect("localhost:7233", namespace="default")

    handle = await client.start_workflow(
        ComplaintResearchWorkflow.run,
        ComplaintInput(complaint_id="CMP0001", policy_number="POL-88421"),
        id="complaint-CMP0001",
        task_queue="complaint-research-task-queue",
    )

    print(f"Started workflow. Workflow ID: {handle.id}")
    print("Open http://localhost:8233 to watch it run.")
    print("It will pause on the NIGO step until you send the resolve_nigo signal.")


if __name__ == "__main__":
    asyncio.run(main())
