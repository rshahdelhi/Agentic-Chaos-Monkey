from __future__ import annotations

import argparse

from .chaos import ChaosWorkflow, FAULTY_V2_EXPERIMENT
from .demo import DemoEnvironment
from .domain import Incident
from .observability import configure_tracing
from .workflow import IncidentWorkflow


def main() -> None:
    configure_tracing()
    parser = argparse.ArgumentParser(description="Run the safe in-memory incident demo")
    parser.add_argument(
        "--approve-rollback",
        action="store_true",
        help="approve the medium-risk rollback runbook",
    )
    parser.add_argument(
        "--inject-chaos",
        action="store_true",
        help="start healthy v1 and inject the bounded faulty-v2 experiment",
    )
    args = parser.parse_args()

    environment = DemoEnvironment(
        initial_version="v1" if args.inject_chaos else "v2"
    )
    workflow = IncidentWorkflow(environment, environment, environment)
    if args.inject_chaos:
        incident = ChaosWorkflow(environment, workflow).run(
            FAULTY_V2_EXPERIMENT,
            Incident("demo-faulty-v2"),
            approved=args.approve_rollback,
        )
    else:
        incident = workflow.run(
            Incident("demo-faulty-v2"), approved=args.approve_rollback
        )
    for event in incident.timeline:
        print(event)
    print(f"status={incident.status}")
