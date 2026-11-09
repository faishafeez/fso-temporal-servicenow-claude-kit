"""
Activities for the Complaint Research workflow.

Each function here is a stand-in for a real system call. For the demo they
return mock data instantly (with a short sleep to simulate latency). When
you're ready to connect this to real data, replace the body of each function
with an actual HTTP call — most likely to ServiceNow's Table API, or to
whatever policy/claims/SIU systems you're pulling from in real life.

Nothing about the Workflow (workflow.py) needs to change when you do that —
that's the whole point of the durability boundary Temporal draws.
"""

import asyncio
from temporalio import activity


@activity.defn
async def pull_complaint_history(policy_number: str) -> dict:
    activity.logger.info(f"Pulling complaint history for policy {policy_number}")
    await asyncio.sleep(1)
    return {
        "policy_number": policy_number,
        "prior_complaints": 1,
        "last_complaint_date": "2025-03-14",
        "summary": "One prior billing complaint, resolved without escalation.",
    }


@activity.defn
async def check_fraud_signals(policy_number: str) -> dict:
    activity.logger.info(f"Running SIU fraud-signal check for policy {policy_number}")
    await asyncio.sleep(1)
    return {
        "policy_number": policy_number,
        "siu_flag": False,
        "risk_score": "low",
    }


@activity.defn
async def pull_policy_documents(policy_number: str) -> dict:
    activity.logger.info(f"Pulling policy documents for policy {policy_number}")
    await asyncio.sleep(1)
    # This simulates the NIGO (Not In Good Order): the policy file is missing
    # its endorsement effective date, so there's nothing to retry — the data
    # simply isn't there yet. Raising here is what triggers the workflow's
    # NIGO branch (see workflow.py).
    raise ValueError("NIGO: policy file is missing its endorsement effective date")


@activity.defn
async def create_partial_payment(complaint_id: str) -> dict:
    activity.logger.info(f"Creating partial payment for complaint {complaint_id}")
    await asyncio.sleep(1)
    return {
        "complaint_id": complaint_id,
        "payment_status": "created",
        "amount": 850.00,
    }
