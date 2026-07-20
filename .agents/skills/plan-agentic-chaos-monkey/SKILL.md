---
name: plan-agentic-chaos-monkey
description: Create phased, implementation-ready plans for Agentic Chaos Monkey, a Kubernetes resilience-validation platform that injects controlled failures and uses Google ADK agents to detect, investigate, govern, remediate, and verify incidents. Use when planning the project architecture, MVP or demo scope, chaos experiments, observability, agent responsibilities, policy and approval controls, runbooks, recovery verification, testing, rollout, or future resilience features.
---

# Plan Agentic Chaos Monkey

Produce a plan that preserves the closed loop:

`Detect -> Investigate -> Decide -> Approve -> Act -> Verify -> Learn`

Do not treat command completion as recovery. Require service-health verification and an auditable incident timeline.

## Gather Context

Inspect the repository before planning. Identify the current stack, manifests, application behavior, telemetry, tests, deployment workflow, and existing runbooks. Distinguish implemented capabilities from proposed ones.

Read [project-model.md](references/project-model.md) for the intended system boundaries, safety policy, core demo, and terminology. Read [plan-template.md](references/plan-template.md) before drafting the final plan.

State assumptions only when the repository and request do not resolve them. Ask for input only when a choice materially changes architecture, safety, cost, or delivery scope.

## Define the Outcome

Translate the request into observable success criteria. Specify:

- Target failure scenario and blast radius
- Signals that detect the incident
- Evidence required for diagnosis
- Allowed remediation runbook
- Risk class and approval behavior
- Health thresholds and stability window for verification
- Audit records and demo artifacts

Keep an MVP centered on one end-to-end scenario unless the user requests broader coverage. Prefer the faulty `v2` deployment followed by an approved rollback to healthy `v1`.

## Design the Plan

Organize work into vertical milestones that each produce a testable capability. Cover relevant layers:

1. Sample application and local Kubernetes environment
2. Controlled, reversible chaos injection
3. Logs, metrics, Kubernetes events, and deployment history
4. Incident correlation and evidence schema
5. Google ADK investigation, policy, remediation, and verification agents
6. Approved runbooks and least-privilege tool adapters
7. Risk classification and human approval gates
8. Post-remediation health verification and escalation
9. Incident timeline, scoring, tests, and demo workflow

For every task, name the component or likely file area, the change, dependencies, validation method, and completion criterion. Mark parallelizable work and the critical path when useful.

## Apply Safety Constraints

- Bound each experiment by namespace, target, duration, and rollback path.
- Prefer typed, allowlisted operations over arbitrary shell execution.
- Separate investigation, policy, remediation, and verification responsibilities.
- Make low-confidence diagnosis lead to more evidence or escalation, not mutation.
- Require explicit approval for rollback and other medium-risk actions unless policy says otherwise.
- Keep high-risk actions recommendation-only and prohibit destructive infrastructure actions.
- Include timeouts, idempotency, retries with limits, cancellation, and failure recording.
- Avoid production credentials or production targets in the initial plan.

## Plan Validation

Include tests at four levels:

- Unit: policies, evidence correlation, confidence rules, and runbook selection
- Integration: Kubernetes/tool adapters, telemetry queries, approvals, and agent handoffs
- End-to-end: inject failure, detect, diagnose, approve, remediate, and verify
- Safety: denied actions, expired approvals, excessive blast radius, low confidence, failed remediation, and verification timeout

Define measurable acceptance criteria such as detection latency, diagnosis evidence quality, approval enforcement, recovery time, readiness, error rate, latency, replica availability, and stability-window duration.

## Produce the Deliverable

Use the structure in [plan-template.md](references/plan-template.md). Keep the plan decision-complete but adaptable to repository discoveries. Clearly separate MVP, hardening, and future work. End with unresolved decisions only if they genuinely block implementation.
