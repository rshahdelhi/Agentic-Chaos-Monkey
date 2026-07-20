from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum


class IncidentStatus(StrEnum):
    DETECTED = "detected"
    AWAITING_APPROVAL = "awaiting_approval"
    REMEDIATING = "remediating"
    RESOLVED = "resolved"
    ESCALATED = "escalated"


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    PROHIBITED = "prohibited"


class PolicyDecision(StrEnum):
    AUTOMATIC = "automatic"
    REQUIRE_APPROVAL = "require_approval"
    RECOMMEND_ONLY = "recommend_only"
    DENY = "deny"


class ChaosFault(StrEnum):
    FAULTY_DEPLOYMENT = "faulty_deployment"


@dataclass(frozen=True)
class ChaosExperiment:
    name: str
    fault: ChaosFault
    namespace: str
    target: str
    max_duration_seconds: int
    rollback_runbook: str

    def validate(self) -> None:
        if self.namespace != "chaos-demo":
            raise ValueError("Chaos experiments are restricted to the chaos-demo namespace")
        if self.target != "deployment/sample-app":
            raise ValueError("Chaos target is not allowlisted")
        if not 1 <= self.max_duration_seconds <= 300:
            raise ValueError("Chaos duration must be between 1 and 300 seconds")
        if self.rollback_runbook != "rollback_deployment":
            raise ValueError("Chaos experiment requires the approved rollback runbook")


@dataclass(frozen=True)
class Evidence:
    source: str
    summary: str
    observed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class Diagnosis:
    probable_cause: str
    confidence: float
    evidence: tuple[Evidence, ...]
    alternatives: tuple[str, ...] = ()


@dataclass(frozen=True)
class RemediationAction:
    runbook: str
    target: str
    parameters: dict[str, str] = field(default_factory=dict)


@dataclass
class Incident:
    incident_id: str
    status: IncidentStatus = IncidentStatus.DETECTED
    diagnosis: Diagnosis | None = None
    proposed_action: RemediationAction | None = None
    timeline: list[str] = field(default_factory=list)

    def record(self, event: str) -> None:
        timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
        self.timeline.append(f"{timestamp} {event}")
