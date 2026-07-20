from dataclasses import dataclass

from .domain import PolicyDecision, RemediationAction, RiskLevel


@dataclass(frozen=True)
class PolicyResult:
    risk: RiskLevel
    decision: PolicyDecision
    reason: str


_POLICY: dict[str, PolicyResult] = {
    "collect_telemetry": PolicyResult(
        RiskLevel.LOW, PolicyDecision.AUTOMATIC, "Read-only evidence collection"
    ),
    "restart_pod": PolicyResult(
        RiskLevel.LOW, PolicyDecision.AUTOMATIC, "Single-pod restart is bounded"
    ),
    "scale_deployment": PolicyResult(
        RiskLevel.MEDIUM,
        PolicyDecision.REQUIRE_APPROVAL,
        "Scaling changes service capacity",
    ),
    "rollback_deployment": PolicyResult(
        RiskLevel.MEDIUM,
        PolicyDecision.REQUIRE_APPROVAL,
        "Rollback changes the running release",
    ),
    "change_database": PolicyResult(
        RiskLevel.HIGH,
        PolicyDecision.RECOMMEND_ONLY,
        "Database changes require an operator",
    ),
    "delete_infrastructure": PolicyResult(
        RiskLevel.PROHIBITED, PolicyDecision.DENY, "Destructive action is prohibited"
    ),
}


def evaluate(action: RemediationAction) -> PolicyResult:
    return _POLICY.get(
        action.runbook,
        PolicyResult(
            RiskLevel.PROHIBITED,
            PolicyDecision.DENY,
            "Runbook is not allowlisted",
        ),
    )
