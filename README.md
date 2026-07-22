# Agentic Chaos Monkey

Break it safely. Diagnose it intelligently. Heal it automatically.

Agentic Chaos Monkey is a resilience-validation platform for testing whether an
agentic system can detect, investigate, govern, remediate, and verify a
controlled incident. The initial scaffold models the full lifecycle without
granting agents arbitrary infrastructure access.

## Presentation

[View the editable Agentic Chaos Monkey presentation in Figma Slides](https://www.figma.com/slides/G2UgkQLf482Zjgij640H0n).

See [PRESENTATION.md](PRESENTATION.md) for the deck outline and submission notes.

## Quick start

```powershell
uv sync
uv run agentic-chaos-monkey
uv run python -m unittest discover -s tests
```

The demo runs an in-memory faulty-deployment scenario. A rollback is classified
as medium risk, so it stops at an approval gate unless `--approve-rollback` is
provided:

```powershell
uv run agentic-chaos-monkey --approve-rollback
```

Run the complete bounded chaos loop from a healthy `v1` baseline:

```powershell
uv run agentic-chaos-monkey --inject-chaos --approve-rollback
```

Launch the Streamlit control panel:

```powershell
uv run streamlit run src/agentic_chaos_monkey/streamlit_app.py
```

The UI exposes only the allowlisted demo experiment and uses the same policy,
approval, remediation, verification, cleanup, tracing, and audit workflow as
the CLI.

Without `--approve-rollback`, the experiment records the human approval gate
and immediately cleans up the fault because the in-memory CLI has no persistent
timeout controller. The chaos catalog currently permits only `faulty-v2-deployment` in the
`chaos-demo` namespace against `deployment/sample-app`, with a maximum duration
of five minutes and a typed rollback path.

## Project layout

- `domain.py` defines incidents, evidence, diagnoses, actions, and audit events.
- `policy.py` contains the allowlisted remediation policy.
- `workflow.py` coordinates detect, investigate, decide, approve, act, verify,
  and learn stages behind typed ports.
- `demo.py` supplies safe in-memory adapters for the primary `v2` to `v1`
  rollback scenario.
- `tests/` validates approval enforcement and verified recovery.

Kubernetes and persistent audit storage remain adapter implementations for
subsequent milestones. The current demo uses an in-memory environment and
OpenTelemetry spans.

## Gemini and Google ADK

The investigation agent uses Google ADK with Gemini. Copy `.env.example` to
`.env`, then replace the placeholder with a key created in Google AI Studio:

```powershell
Copy-Item .env.example .env
# Edit .env and set GEMINI_API_KEY. Never commit this file.
```

Alternatively, set the key for the current PowerShell session:

```powershell
$env:GEMINI_API_KEY = "your-key"
```

ADK also accepts `GOOGLE_API_KEY`; when both variables exist, it takes
precedence. The model defaults to `gemini-flash-latest` and can be overridden
with `GEMINI_MODEL`.

Start the ADK development UI from the repository root. The coordinator delegates
to dedicated chaos, detection, investigation, policy, remediation, and
verification agents:

```powershell
uv run adk web src
```

The initial Gemini agent is investigation-only. It receives no remediation or
shell tools; mutations remain behind the deterministic policy and approval
workflow.

## OpenTelemetry tracing

The incident workflow emits spans for investigation, remediation, verification,
and the overall lifecycle. To inspect spans locally:

```powershell
$env:OTEL_TRACES_EXPORTER = "console"
uv run agentic-chaos-monkey --approve-rollback
```

To send spans to an OTLP-compatible collector:

```powershell
$env:OTEL_TRACES_EXPORTER = "otlp"
$env:OTEL_EXPORTER_OTLP_ENDPOINT = "http://localhost:4317"
uv run agentic-chaos-monkey --approve-rollback
```

OpenTelemetry's standard `OTEL_*` variables can configure headers, TLS, and
resource attributes without code changes.
