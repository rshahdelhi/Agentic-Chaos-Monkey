"""Streamlit control panel for the bounded Agentic Chaos Monkey demo."""

from __future__ import annotations

from dataclasses import asdict

import streamlit as st

from agentic_chaos_monkey.chaos import ChaosWorkflow, FAULTY_V2_EXPERIMENT
from agentic_chaos_monkey.demo import DemoEnvironment
from agentic_chaos_monkey.domain import Incident
from agentic_chaos_monkey.observability import configure_tracing
from agentic_chaos_monkey.workflow import IncidentWorkflow


AGENTS = (
    ("Chaos", "Validates experiment scope and rollback boundaries."),
    ("Detection", "Establishes the incident from observed signals."),
    ("Investigation", "Correlates evidence and assigns confidence."),
    ("Policy", "Classifies risk and enforces approval requirements."),
    ("Remediation", "Executes only the typed, approved runbook."),
    ("Verification", "Independently confirms service recovery."),
)


def _run_experiment(approved: bool) -> dict[str, object]:
    environment = DemoEnvironment(initial_version="v1")
    workflow = ChaosWorkflow(
        environment,
        IncidentWorkflow(environment, environment, environment),
    )
    incident = workflow.run(
        FAULTY_V2_EXPERIMENT,
        Incident("streamlit-faulty-v2"),
        approved=approved,
    )
    return {
        "status": incident.status.value,
        "final_version": environment.version,
        "ready": environment.ready,
        "approved": approved,
        "timeline": incident.timeline,
        "diagnosis": asdict(incident.diagnosis) if incident.diagnosis else None,
        "action": asdict(incident.proposed_action)
        if incident.proposed_action
        else None,
    }


def _render_result(result: dict[str, object]) -> None:
    status = str(result["status"])
    if status == "resolved":
        st.success("The injected failure was rolled back and recovery was verified.")
    elif status == "awaiting_approval":
        st.warning(
            "Rollback approval was not granted. The demo fault was cleaned up "
            "automatically and the incident remains at the approval gate."
        )
    else:
        st.error(f"The incident ended with status: {status}")

    diagnosis = result.get("diagnosis") or {}
    columns = st.columns(4)
    columns[0].metric("Incident status", status.replace("_", " ").title())
    columns[1].metric("Final release", str(result["final_version"]))
    columns[2].metric("Service ready", "Yes" if result["ready"] else "No")
    columns[3].metric(
        "Confidence",
        f"{float(diagnosis.get('confidence', 0)):.0%}" if diagnosis else "—",
    )

    left, right = st.columns((1, 1))
    with left:
        st.subheader("Investigation evidence")
        if diagnosis:
            st.write(diagnosis["probable_cause"])
            for item in diagnosis["evidence"]:
                with st.expander(str(item["source"]).replace("-", " ").title()):
                    st.write(item["summary"])
                    st.caption(f"Observed at {item['observed_at']}")
            alternatives = diagnosis.get("alternatives", ())
            if alternatives:
                st.caption("Alternatives: " + ", ".join(alternatives))
        else:
            st.info("No diagnosis was produced.")

    with right:
        st.subheader("Auditable timeline")
        for index, event in enumerate(result["timeline"], start=1):
            st.markdown(f"**{index}.** `{event}`")


def main() -> None:
    st.set_page_config(
        page_title="Agentic Chaos Monkey",
        page_icon="🐒",
        layout="wide",
    )
    configure_tracing()

    st.title("Agentic Chaos Monkey")
    st.caption("Break it safely. Diagnose it intelligently. Verify the recovery.")

    with st.sidebar:
        st.header("Experiment controls")
        st.text_input("Experiment", FAULTY_V2_EXPERIMENT.name, disabled=True)
        st.text_input("Namespace", FAULTY_V2_EXPERIMENT.namespace, disabled=True)
        st.text_input("Target", FAULTY_V2_EXPERIMENT.target, disabled=True)
        st.number_input(
            "Maximum duration (seconds)",
            value=FAULTY_V2_EXPERIMENT.max_duration_seconds,
            disabled=True,
        )
        approved = st.checkbox(
            "Approve rollback to v1",
            help="Rollback is medium risk and requires explicit human approval.",
        )
        run_clicked = st.button(
            "Inject bounded failure",
            type="primary",
            use_container_width=True,
        )
        st.caption("Demo only · in-memory adapter · no Kubernetes access")

    st.subheader("Multi-agent recovery team")
    agent_columns = st.columns(3)
    for index, (name, responsibility) in enumerate(AGENTS):
        with agent_columns[index % 3]:
            with st.container(border=True):
                st.markdown(f"**{name} agent**")
                st.caption(responsibility)

    st.divider()
    if run_clicked:
        try:
            with st.spinner("Running the governed chaos and recovery loop…"):
                st.session_state["last_result"] = _run_experiment(approved)
        except Exception as exc:  # Streamlit must surface adapter/policy failures.
            st.exception(exc)

    result = st.session_state.get("last_result")
    if result:
        _render_result(result)
    else:
        st.info(
            "Configure rollback approval in the sidebar, then inject the "
            "allowlisted faulty-v2 experiment."
        )


if __name__ == "__main__":
    main()
