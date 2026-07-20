from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from opentelemetry import trace

from .domain import (
    Diagnosis,
    Incident,
    IncidentStatus,
    PolicyDecision,
    RemediationAction,
)
from .policy import evaluate


tracer = trace.get_tracer(__name__)


class Investigator(Protocol):
    def investigate(self, incident: Incident) -> Diagnosis: ...


class Remediator(Protocol):
    def execute(self, action: RemediationAction) -> None: ...


class Verifier(Protocol):
    def is_healthy(self, incident: Incident) -> bool: ...


@dataclass
class IncidentWorkflow:
    investigator: Investigator
    remediator: Remediator
    verifier: Verifier

    def run(self, incident: Incident, *, approved: bool = False) -> Incident:
        with tracer.start_as_current_span("incident.workflow") as span:
            span.set_attribute("incident.id", incident.incident_id)
            span.set_attribute("remediation.approved", approved)
            result = self._run(incident, approved=approved)
            span.set_attribute("incident.status", result.status.value)
            return result

    def _run(self, incident: Incident, *, approved: bool) -> Incident:
        incident.record("incident.detected")
        with tracer.start_as_current_span("incident.investigate"):
            incident.diagnosis = self.investigator.investigate(incident)
        incident.record(
            f"diagnosis.completed confidence={incident.diagnosis.confidence:.2f}"
        )

        if incident.diagnosis.confidence < 0.75:
            incident.status = IncidentStatus.ESCALATED
            incident.record("diagnosis.low_confidence escalation.required")
            return incident

        action = RemediationAction(
            runbook="rollback_deployment",
            target="deployment/sample-app",
            parameters={"revision": "v1"},
        )
        incident.proposed_action = action
        result = evaluate(action)
        incident.record(f"policy.{result.decision} risk={result.risk}")

        if result.decision is PolicyDecision.DENY:
            incident.status = IncidentStatus.ESCALATED
            return incident
        if result.decision is PolicyDecision.RECOMMEND_ONLY:
            incident.status = IncidentStatus.ESCALATED
            return incident
        if result.decision is PolicyDecision.REQUIRE_APPROVAL and not approved:
            incident.status = IncidentStatus.AWAITING_APPROVAL
            incident.record("approval.required")
            return incident

        incident.status = IncidentStatus.REMEDIATING
        incident.record("remediation.started")
        with tracer.start_as_current_span("incident.remediate") as span:
            span.set_attribute("runbook.name", action.runbook)
            span.set_attribute("remediation.target", action.target)
            self.remediator.execute(action)
        incident.record("remediation.command_completed")

        with tracer.start_as_current_span("incident.verify"):
            is_healthy = self.verifier.is_healthy(incident)
        if is_healthy:
            incident.status = IncidentStatus.RESOLVED
            incident.record("verification.healthy incident.resolved")
        else:
            incident.status = IncidentStatus.ESCALATED
            incident.record("verification.failed escalation.required")
        return incident
