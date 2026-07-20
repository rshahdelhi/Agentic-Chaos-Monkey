from .domain import (
    ChaosExperiment,
    ChaosFault,
    Diagnosis,
    Evidence,
    Incident,
    RemediationAction,
)


class DemoEnvironment:
    def __init__(self, *, initial_version: str = "v2") -> None:
        self.version = initial_version
        self.ready = initial_version == "v1"

    def inject(self, experiment: ChaosExperiment) -> None:
        experiment.validate()
        if experiment.fault is not ChaosFault.FAULTY_DEPLOYMENT:
            raise ValueError("Demo environment only supports faulty deployment chaos")
        if not self.ready or self.version != "v1":
            raise RuntimeError("Chaos requires a healthy v1 baseline")
        self.version = "v2"
        self.ready = False

    def cleanup(self, experiment: ChaosExperiment) -> None:
        experiment.validate()
        self.version = "v1"
        self.ready = True

    def investigate(self, incident: Incident) -> Diagnosis:
        return Diagnosis(
            probable_cause="Faulty v2 configuration caused readiness failures",
            confidence=0.95,
            evidence=(
                Evidence("deployment-history", "v2 deployed immediately before failure"),
                Evidence("kubernetes-events", "readiness probe failures on v2 pods"),
                Evidence("application-metrics", "error rate and latency increased"),
            ),
            alternatives=("dependency outage", "cluster resource pressure"),
        )

    def execute(self, action: RemediationAction) -> None:
        if action.runbook != "rollback_deployment":
            raise ValueError("Demo environment only supports the rollback runbook")
        self.version = action.parameters["revision"]
        self.ready = self.version == "v1"

    def is_healthy(self, incident: Incident) -> bool:
        return self.ready and self.version == "v1"
