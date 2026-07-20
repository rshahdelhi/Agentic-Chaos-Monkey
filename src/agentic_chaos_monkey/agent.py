"""Google ADK multi-agent application for governed chaos recovery."""

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

from .settings import gemini_model_name


def _model() -> Gemini:
    return Gemini(
        model=gemini_model_name(),
        retry_options=types.HttpRetryOptions(attempts=3),
    )


chaos_agent = Agent(
    name="chaos_agent",
    model=_model(),
    description="Plans only bounded, reversible chaos experiments.",
    instruction="""
Validate a chaos request before it can run. The MVP permits only the
faulty-v2-deployment experiment in namespace chaos-demo, targeting exactly
deployment/sample-app, for at most 300 seconds, with rollback_deployment as
the cleanup path. Reject broader targets, production namespaces, destructive
actions, arbitrary commands, or missing rollback paths. You advise only; the
typed application adapter performs injection.
""".strip(),
)

detection_agent = Agent(
    name="detection_agent",
    model=_model(),
    description="Detects incidents and assembles timestamped signals.",
    instruction="""
Determine whether supplied readiness, error-rate, latency, Kubernetes-event,
and deployment-history signals establish an incident. Never invent evidence.
Return the incident signals and their timestamps for investigation.
""".strip(),
)

investigation_agent = Agent(
    name="investigation_agent",
    model=_model(),
    description="Correlates incident evidence and recommends a governed next step.",
    instruction="""
Correlate only supplied evidence. Return probable cause, supporting evidence,
confidence from 0.0 to 1.0, alternatives, and a recommended allowlisted
runbook. Below 0.75 confidence, request more evidence or escalation. Never
execute remediation or generate shell commands.
""".strip(),
)

policy_agent = Agent(
    name="policy_agent",
    model=_model(),
    description="Classifies proposed actions and enforces approval policy.",
    instruction="""
Apply this policy exactly: read-only evidence collection and one unhealthy-pod
restart are low risk; scaling and rollback are medium risk and require human
approval; database changes are recommendation-only; infrastructure deletion
and non-allowlisted actions are denied. Report the decision and reason. Never
claim approval was granted unless it is present in the incident record.
""".strip(),
)

remediation_agent = Agent(
    name="remediation_agent",
    model=_model(),
    description="Selects typed remediation runbooks after policy approval.",
    instruction="""
Proceed only when policy allows the exact typed action and any required,
unexpired human approval is present. The MVP action is rollback_deployment for
deployment/sample-app to revision v1. Never produce or execute arbitrary shell
commands. Report the requested runbook outcome for independent verification.
""".strip(),
)

verification_agent = Agent(
    name="verification_agent",
    model=_model(),
    description="Independently verifies sustained recovery after remediation.",
    instruction="""
Recovery requires healthy endpoint results, ready expected replicas, normal
error rate and latency, and stability for the configured window. Command
completion alone is not recovery. If evidence is incomplete or unhealthy,
mark verification failed and escalate.
""".strip(),
)

root_agent = Agent(
    name="chaos_recovery_coordinator",
    model=_model(),
    description="Coordinates the safe Detect-Investigate-Decide-Approve-Act-Verify loop.",
    instruction="""
Coordinate the specialist agents without collapsing their responsibilities.
For a chaos run: ask chaos_agent to validate scope, detection_agent to establish
the incident, investigation_agent to correlate evidence, policy_agent to make
the binding risk decision, remediation_agent to select a typed approved
runbook, and verification_agent to judge recovery. Stop at an approval gate
when required. Preserve a complete auditable timeline and never treat command
completion as recovery.
""".strip(),
    sub_agents=[
        chaos_agent,
        detection_agent,
        investigation_agent,
        policy_agent,
        remediation_agent,
        verification_agent,
    ],
)

app = App(root_agent=root_agent, name="agentic_chaos_monkey")
