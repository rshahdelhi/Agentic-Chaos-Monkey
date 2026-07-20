import unittest

from agentic_chaos_monkey.demo import DemoEnvironment
from agentic_chaos_monkey.domain import Incident, IncidentStatus
from agentic_chaos_monkey.workflow import IncidentWorkflow


class IncidentWorkflowTests(unittest.TestCase):
    def test_rollback_waits_for_approval(self) -> None:
        environment = DemoEnvironment()
        incident = IncidentWorkflow(environment, environment, environment).run(
            Incident("test-1")
        )

        self.assertEqual(incident.status, IncidentStatus.AWAITING_APPROVAL)
        self.assertEqual(environment.version, "v2")

    def test_approved_rollback_requires_health_verification(self) -> None:
        environment = DemoEnvironment()
        incident = IncidentWorkflow(environment, environment, environment).run(
            Incident("test-2"), approved=True
        )

        self.assertEqual(incident.status, IncidentStatus.RESOLVED)
        self.assertEqual(environment.version, "v1")
        self.assertIn("verification.healthy", incident.timeline[-1])


if __name__ == "__main__":
    unittest.main()
