"""
ComplaintResearchWorkflow

This is the "Research" lane of the complaint storyboard, as an actual
Temporal Workflow:

  1. Pull complaint history        (durable activity, retries on failure)
  2. Check SIU fraud signals        (durable activity, retries on failure)
  3. Pull policy documents          --> hits a NIGO (missing endorsement
                                         date). This is NOT retried, because
                                         retrying can't produce data that
                                         doesn't exist. Instead the workflow
                                         pauses and waits for a Signal.
  4. Create partial payment         (durable activity, runs once FSO has
                                         resolved the NIGO and the workflow
                                         resumes)

The ServiceNow side of this (a UI Action + a Business Rule) is what's
expected to:
  - call research_status() (a Query) to see whether a NIGO is blocking things
  - open a task for the missing document
  - once that task/field work is done, send the `resolve_nigo` Signal back
    in, with the missing endorsement date

That hand-off is the whole point of this demo: Temporal can't get unstuck on
its own here. ServiceNow's human/task layer is what gets it moving again.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from activities import (
        pull_complaint_history,
        check_fraud_signals,
        pull_policy_documents,
        create_partial_payment,
    )


@dataclass
class ComplaintInput:
    complaint_id: str
    policy_number: str


@dataclass
class NigoResolution:
    endorsement_date: str


@workflow.defn
class ComplaintResearchWorkflow:
    def __init__(self) -> None:
        self._complaint_history_done: bool = False
        self._fraud_check_done: bool = False
        self._fraud_risk_score: str = ""
        self._document_review_complete: bool = False
        self._nigo_flagged: bool = False
        self._nigo_reason: str = ""
        self._nigo_resolved: bool = False
        self._endorsement_date: str | None = None

    @workflow.run
    async def run(self, input: ComplaintInput) -> dict:
        complaint_history = await workflow.execute_activity(
            pull_complaint_history,
            input.policy_number,
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=RetryPolicy(maximum_attempts=5),
        )
        self._complaint_history_done = True

        fraud_signal = await workflow.execute_activity(
            check_fraud_signals,
            input.policy_number,
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=RetryPolicy(maximum_attempts=5),
        )
        self._fraud_check_done = True
        self._fraud_risk_score = fraud_signal["risk_score"]

        try:
            policy_doc = await workflow.execute_activity(
                pull_policy_documents,
                input.policy_number,
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=RetryPolicy(maximum_attempts=1),  # no point retrying a NIGO
            )
        except Exception:
            self._nigo_flagged = True
            self._nigo_reason = "Missing endorsement effective date on policy file"
            workflow.logger.info(f"NIGO flagged, pausing: {self._nigo_reason}")

            # This is where the workflow genuinely stops and waits. No polling,
            # no busy loop on Temporal's side — it costs nothing to sit here
            # until ServiceNow sends the Signal back.
            await workflow.wait_condition(lambda: self._nigo_resolved)

            policy_doc = {
                "endorsement_date": self._endorsement_date,
                "status": "completed_after_nigo_resolution",
            }

        self._document_review_complete = True

        payment = await workflow.execute_activity(
            create_partial_payment,
            input.complaint_id,
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=RetryPolicy(maximum_attempts=5),
        )

        return {
            "complaint_history": complaint_history,
            "fraud_signal": fraud_signal,
            "policy_doc": policy_doc,
            "payment": payment,
            "nigo_occurred": self._nigo_flagged,
        }

    @workflow.signal
    def resolve_nigo(self, resolution: NigoResolution) -> None:
        self._endorsement_date = resolution.endorsement_date
        self._nigo_resolved = True

    @workflow.query
    def research_status(self) -> dict:
        if self._nigo_flagged and not self._nigo_resolved:
            document_status = "NIGO-Missing Documents"
        elif self._document_review_complete:
            document_status = "IGO"
        else:
            document_status = ""

        return {
            "complaint_history_done": self._complaint_history_done,
            "fraud_check_done": self._fraud_check_done,
            "fraud_risk_score": self._fraud_risk_score,
            "document_review_complete": self._document_review_complete,
            "document_status": document_status,
            "nigo_flagged": self._nigo_flagged,
            "nigo_resolved": self._nigo_resolved,
            "nigo_reason": self._nigo_reason,
        }
