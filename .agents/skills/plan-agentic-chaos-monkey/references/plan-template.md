# Plan Output Template

## Objective

State the user-visible outcome and the selected incident scenario.

## Current State and Assumptions

Summarize relevant repository findings, constraints, and explicitly labeled assumptions.

## Scope

List MVP inclusions, exclusions, target environment, blast radius, and safety boundaries.

## Architecture and Decisions

Describe components, data flow, agent boundaries, evidence schema, runbook interface, policy decisions, approval flow, and verification contract. Explain consequential tradeoffs.

## Milestones

For each milestone include:

- Outcome
- Components or likely file areas
- Ordered implementation tasks
- Dependencies and parallel work
- Validation and acceptance criteria
- Risks and rollback or fallback

Prefer vertical milestones that finish a demonstrable slice over isolated infrastructure phases.

## Test Matrix

Map happy paths and failure paths to unit, integration, end-to-end, and safety tests. Include rejected actions and failed recovery verification.

## Demo Runbook

Specify setup, fault injection, expected signals, approval interaction, remediation, verification window, incident timeline, and cleanup.

## Delivery Sequence

Separate MVP, hardening, and future extensions. Identify the critical path and any external prerequisites.

## Open Decisions

Include only unresolved choices that materially block or change implementation. Recommend a default for each.
