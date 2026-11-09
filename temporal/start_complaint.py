"""
Start a research workflow for a specific complaint number — matching
whatever your real ServiceNow record's `number` field actually is
(e.g. INSCMPL0001035, or whatever your table's numbering scheme produces).

Usage:
    python start_complaint.py INSCMPL0001035
    python start_complaint.py INSCMPL0001035 POL-99001   (custom policy number too)

If you don't pass any arguments, it defaults to a sample ID — mainly
useful for a first manual test.
"""

import asyncio
import sys
from temporalio.client import Client

from workflow import ComplaintResearchWorkflow, ComplaintInput


async def main():
    complaint_id = sys.argv[1] if len(sys.argv) > 1 else "INSCMPL0001035"
    policy_number = sys.argv[2] if len(sys.argv) > 2 else "POL-88421"

    client = await Client.connect("localhost:7233", namespace="default")
    handle = await client.start_workflow(
        ComplaintResearchWorkflow.run,
        ComplaintInput(complaint_id=complaint_id, policy_number=policy_number),
        id=f"complaint-{complaint_id}",
        task_queue="complaint-research-task-queue",
    )
    print(f"Started workflow. Workflow ID: {handle.id}")
    print("Open http://localhost:8233 to watch it run.")


if __name__ == "__main__":
    asyncio.run(main())
