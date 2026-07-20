# Agentic Chaos Monkey Project Model

## Product Goal

Create a controlled environment that tests whether people, automation, and AI agents can recover a service safely after a deliberate failure. The system must inject a fault, detect and diagnose it from evidence, select a governed action, obtain approval when required, execute an allowlisted runbook, verify user-visible recovery, and record the full timeline.

## Core Architecture

| Layer | Responsibility |
|---|---|
| Chaos injection | Introduce bounded, reversible Kubernetes failures |
| Observability | Supply logs, metrics, health signals, Kubernetes events, and deployment history |
| Investigation agent | Correlate evidence and report likely cause, confidence, alternatives, and next step |
| Policy agent | Allow, require approval, recommend only, or deny an action |
| Remediation agent | Execute only an approved, typed runbook |
| Verification agent | Independently confirm sustained service recovery |
| Incident record | Preserve evidence, decisions, approvals, actions, and outcomes |

Google Agent Development Kit (ADK) coordinates the specialized agents. Keep responsibilities separate so no single agent has unrestricted environmental control.

## Initial Failure Catalog

- Terminate an application pod
- Deploy an unhealthy version
- Add artificial latency
- Cause readiness-probe failures
- Apply incorrect environment configuration
- Reduce available replicas

Limit early plans to a small, understandable catalog. Every experiment needs prerequisites, target scope, maximum duration, abort conditions, cleanup, and expected signals.

## Evidence Model

Correlate evidence on a common incident timeline:

- Application error rate and structured logs
- Request latency and health endpoint results
- Pod readiness, restarts, and replica availability
- Readiness and liveness probe failures
- Kubernetes events
- Recent deployment and configuration changes

A diagnosis must include supporting evidence, confidence, alternatives, and a recommended next step. Insufficient confidence must trigger more investigation or escalation.

## Risk Policy Baseline

| Action | Risk | Default behavior |
|---|---|---|
| Collect logs and metrics | Low | Automatic |
| Restart one unhealthy pod | Low | Automatic |
| Scale a deployment | Medium | Policy-dependent approval |
| Roll back a deployment | Medium | Human approval required |
| Change database configuration | High | Recommendation only |
| Delete infrastructure | Prohibited | Never allowed |

Use narrowly scoped service accounts, allowlisted tool parameters, immutable audit events, approval expiry, and actor identity. Never substitute generated shell commands for approved runbooks.

## Primary Demo

1. Run healthy application version `v1`.
2. Deploy faulty version `v2` with incorrect configuration.
3. Observe readiness failures, errors, and latency increase.
4. Correlate telemetry and deployment history.
5. Diagnose `v2` as the probable cause with supporting evidence.
6. Recommend rollback to `v1`.
7. Classify rollback as medium risk and request approval.
8. Execute the approved rollback.
9. Verify ready pods, healthy endpoint, normal error rate and latency, expected replicas, and stability over a defined window.
10. Display the complete incident and recovery timeline.

## Planning Priorities

Prioritize the end-to-end demo before expanding failure types. After the MVP, consider OpenTelemetry traces, dependency failures, CPU or memory pressure, SLO and error-budget awareness, CI/CD integration, scheduled game days, historical learning, diagnosis scoring, MTTR, and application resilience scoring.
