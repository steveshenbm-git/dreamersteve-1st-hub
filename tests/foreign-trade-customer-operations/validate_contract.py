"""Deterministic static boundary checks for customer operations."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PLUGIN_ROOT = ROOT / "plugins" / "foreign-trade-customer-operations"
SKILL_ROOT = PLUGIN_ROOT / "skills" / "foreign-trade-customer-operations"


def read(relative: str) -> str:
    return (SKILL_ROOT / relative).read_text(encoding="utf-8")


TEXTS = {
    "skill": read("SKILL.md"),
    "routing": read("references/routing-and-account-state.md"),
    "brief": read("references/communication-brief-production.md"),
    "serious": read("references/serious-case-operation.md"),
    "workbook": read("references/workbook-and-automation.md"),
    "optimization": read("references/optimization-validation.md"),
    "manifest": (PLUGIN_ROOT / ".codex-plugin" / "plugin.json").read_text(
        encoding="utf-8"
    ),
}

RULES: dict[str, tuple[str, tuple[str, ...]]] = {
    "skill.operations_ownership": (
        "skill",
        (
            "outreach_activation",
            "interaction_intake",
            "account_operation",
            "serious_case_operation",
            "不生成任何对外正文",
            "communication_brief_packet",
            "foreign-trade-customer-communication",
        ),
    ),
    "routing.hard_predecessors": (
        "routing",
        (
            "customer_flow_link_v1",
            "validate_customer_flow_transition.py",
            "development_outreach_to_operations_activation",
            "development_reply_to_operations_intake",
            "director_actual_interaction_to_operations_intake",
            "OPERATION_DECISION_READY",
        ),
    ),
    "brief.no_jump": (
        "brief",
        (
            "accepted immediate input receipt",
            "confirmed salesperson draft-request receipt",
            "bind_customer_flow_transition.py",
            "A valid envelope alone is insufficient",
            "communication_brief_blocked_packet",
        ),
    ),
    "workbook.actual_state": (
        "workbook",
        (
            "Only `interaction_evidence_packet` may support actual send or actual reply state",
            "daily_due_draft_review",
            "does not create a communication brief, candidate, workbook write, or send action",
        ),
    ),
    "serious.hard_stop": (
        "serious",
        (
            "Do not admit liability",
            "bound responsible-person decision",
            "decision_state = BLOCKED",
        ),
    ),
    "optimization.boundaries": (
        "optimization",
        (
            "0 external message bodies produced by operations",
            "100% rejection of broken predecessor links",
            "due review never creates a brief or candidate",
        ),
    ),
}

FORBIDDEN = (
    "| `cold_outreach` |",
    "| `unanswered_follow_up` |",
    "| `reply_communication` |",
    "standalone compatibility email workflow",
)


def frontmatter_keys(text: str) -> list[str]:
    if not text.startswith("---\n"):
        return []
    parts = text.split("---", 2)
    return [
        line.split(":", 1)[0].strip()
        for line in parts[1].splitlines()
        if line and not line.startswith((" ", "\t")) and ":" in line
    ]


def diagnostics_for(texts: dict[str, str]) -> list[str]:
    diagnostics: list[str] = []
    for label, (text_key, fragments) in RULES.items():
        missing = [fragment for fragment in fragments if fragment not in texts[text_key]]
        if missing:
            diagnostics.append(f"{label}: missing {missing!r}")
    present = [fragment for fragment in FORBIDDEN if fragment in texts["skill"]]
    if present:
        diagnostics.append(f"skill.stale_routes: forbidden {present!r}")
    if frontmatter_keys(texts["skill"]) != ["name", "description"]:
        diagnostics.append("skill.frontmatter: expected exactly name and description")
    try:
        manifest = json.loads(texts["manifest"])
    except json.JSONDecodeError as error:
        diagnostics.append(f"manifest.json: invalid JSON: {error}")
    else:
        if manifest.get("name") != "foreign-trade-customer-operations":
            diagnostics.append("manifest.name: unexpected plugin name")
        if manifest.get("version") != "0.3.0-beta.1":
            diagnostics.append("manifest.version: unexpected candidate version")
    return diagnostics


def validator_self_check() -> list[str]:
    failures: list[str] = []
    for label, (text_key, fragments) in RULES.items():
        for fragment in fragments:
            mutated = dict(TEXTS)
            mutated[text_key] = mutated[text_key].replace(fragment, "")
            if not any(item.startswith(label + ":") for item in diagnostics_for(mutated)):
                failures.append(f"{label}: accepted removal of {fragment!r}")
    return failures


def main() -> int:
    self_failures = validator_self_check()
    if self_failures:
        for failure in self_failures:
            print(f"FAIL validator.self_check: {failure}")
        return 2
    diagnostics = diagnostics_for(TEXTS)
    if diagnostics:
        for diagnostic in diagnostics:
            print(f"FAIL {diagnostic}")
        return 1
    print("PASS: customer operations owns state, decisions, and briefs without drafting")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
