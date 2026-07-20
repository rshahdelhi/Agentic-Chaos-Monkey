import unittest

from agentic_chaos_monkey.chaos import ChaosWorkflow, FAULTY_V2_EXPERIMENT
from agentic_chaos_monkey.demo import DemoEnvironment
from agentic_chaos_monkey.domain import ChaosExperiment, Incident, IncidentStatus
from agentic_chaos_monkey.workflow import IncidentWorkflow


class ChaosWorkflowTests(unittest.TestCase):
    def test_bounded_chaos_runs_closed_loop_after_approval(self) -> None:
        environment = DemoEnvironment(initial_version="v1")
        workflow = ChaosWorkflow(
            environment,
            IncidentWorkflow(environment, environment, environment),
        )

        incident = workflow.run(
            FAULTY_V2_EXPERIMENT, Incident("chaos-1"), approved=True
        )

        self.assertEqual(incident.status, IncidentStatus.RESOLVED)
        self.assertEqual(environment.version, "v1")
        self.assertIn("chaos.injected", incident.timeline[1])
        self.assertIn("verification.healthy", incident.timeline[-1])

    def test_chaos_stops_at_rollback_approval_gate(self) -> None:
        environment = DemoEnvironment(initial_version="v1")
        workflow = ChaosWorkflow(
            environment,
            IncidentWorkflow(environment, environment, environment),
        )

        incident = workflow.run(FAULTY_V2_EXPERIMENT, Incident("chaos-2"))

        self.assertEqual(incident.status, IncidentStatus.AWAITING_APPROVAL)
        self.assertEqual(environment.version, "v1")
        self.assertIn("chaos.cleanup reason=approval_required", incident.timeline[-1])

    def test_non_allowlisted_namespace_is_rejected_before_injection(self) -> None:
        environment = DemoEnvironment(initial_version="v1")
        invalid = ChaosExperiment(
            **{
                **FAULTY_V2_EXPERIMENT.__dict__,
                "namespace": "production",
            }
        )
        workflow = ChaosWorkflow(
            environment,
            IncidentWorkflow(environment, environment, environment),
        )

        with self.assertRaises(ValueError):
            workflow.run(invalid, Incident("chaos-3"), approved=True)

        self.assertEqual(environment.version, "v1")


if __name__ == "__main__":
    unittest.main()
