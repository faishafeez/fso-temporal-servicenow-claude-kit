"""
Run this to start the worker. Leave it running in its own terminal —
it's what actually executes the workflow and activity code whenever
Temporal Server hands it work.

    python worker.py
"""

import asyncio
import logging

from temporalio.client import Client
from temporalio.worker import Worker

from workflow import ComplaintResearchWorkflow
import activities

logging.basicConfig(level=logging.INFO)


async def main():
    client = await Client.connect("localhost:7233", namespace="default")

    worker = Worker(
        client,
        task_queue="complaint-research-task-queue",
        workflows=[ComplaintResearchWorkflow],
        activities=[
            activities.pull_complaint_history,
            activities.check_fraud_signals,
            activities.pull_policy_documents,
            activities.create_partial_payment,
        ],
    )

    print("Worker started. Listening on task queue 'complaint-research-task-queue'...")
    print("Leave this running. Ctrl+C to stop.")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
