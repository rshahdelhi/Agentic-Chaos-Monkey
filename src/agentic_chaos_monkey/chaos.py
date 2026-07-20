"""Bounded chaos experiments and their closed-loop orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from opentelemetry import trace

from .domain import ChaosExperiment, ChaosFault, Incident, IncidentStatus
from .workflow import IncidentWorkflow


tracer = trace.get_tracer(__name__)

FAULTY_V2_EXPERIMENT = ChaosExperiment(
    name="faulty-v2-deployment",
    fault=ChaosFault.FAULTY_DEPLOYMENT,
    namespace="chaos-demo",
    target="deployment/sample-app",
    max_duration_seconds=300,
    rollback_runbook="rollback_deployment",
)


class ChaosInjector(Protocol):
    def inject(self, experiment: ChaosExperiment) -> None: ...

    def cleanup(self, experiment: ChaosExperiment) -> None: ...


@dataclass
class ChaosWorkflow:
    injector: ChaosInjector
    incident_workflow: IncidentWorkflow

    def run(
        self,
        experiment: ChaosExperiment,
        incident: Incident,
        *,
        approved: bool = False,
    ) -> Incident:
        experiment.validate()
        incident.record(
            "chaos.requested "
            f"experiment={experiment.name} namespace={experiment.namespace} "
            f"target={experiment.target} max_duration={experiment.max_duration_seconds}s"
        )

        with tracer.start_as_current_span("chaos.inject") as span:
            span.set_attribute("chaos.experiment", experiment.name)
            span.set_attribute("chaos.namespace", experiment.namespace)
            span.set_attribute("chaos.target", experiment.target)
            span.set_attribute(
                "chaos.max_duration_seconds", experiment.max_duration_seconds
            )
            self.injector.inject(experiment)
        incident.record(f"chaos.injected fault={experiment.fault.value}")

        try:
            result = self.incident_workflow.run(incident, approved=approved)
        except Exception:
            self.injector.cleanup(experiment)
            incident.record("chaos.cleanup reason=workflow_error")
            raise

        if result.status is IncidentStatus.AWAITING_APPROVAL:
            self.injector.cleanup(experiment)
            result.record("chaos.cleanup reason=approval_required")
        elif result.status is IncidentStatus.ESCALATED:
            self.injector.cleanup(experiment)
            result.record("chaos.cleanup reason=escalation")
        return result
