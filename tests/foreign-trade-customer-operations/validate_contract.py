"""Static contracts for customer operations and communication."""

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
    "cold": read("references/cold-outreach-and-follow-up.md"),
    "reply": read("references/reply-communication.md"),
    "reply_evidence": read("references/reply-evidence-and-contract.md"),
    "special": read("references/special-handling.md"),
    "workbook": read("references/workbook-and-automation.md"),
    "manifest": (PLUGIN_ROOT / ".codex-plugin" / "plugin.json").read_text(
        encoding="utf-8"
    ),
    "config": (ROOT / "tools" / "foreign_trade_automation_config.example.json").read_text(
        encoding="utf-8"
    ),
    "legacy": (
        ROOT
        / "plugins"
        / "foreign-trade-email-assistant"
        / "skills"
        / "foreign-trade-email-assistant"
        / "SKILL.md"
    ).read_text(encoding="utf-8"),
    "readme": (ROOT / "README.md").read_text(encoding="utf-8"),
}


RULES: dict[str, tuple[str, tuple[str, ...]]] = {
    "skill.routes_and_authority": (
        "skill",
        (
            "cold_outreach",
            "unanswered_follow_up",
            "reply_communication",
            "account_operation",
            "salesperson owns customer selection",
            "final wording",
            "restricted-contact approval",
            "Do not send or contact anyone",
        ),
    ),
    "routing.development_and_reply_handoffs": (
        "routing",
        (
            "outreach_handoff_packet",
            "development_return_packet",
            "customer_operations_handoff",
            "trigger_channel",
            "trigger_touch_id",
            "response_reference",
            "sender_identity_status",
            "actual_send_history",
            "reply_return_packet",
            "不得延迟交接",
        ),
    ),
    "routing.priority_and_account_operation": (
        "routing",
        (
            "回复或疑似回复 → 风险暂停",
            "回复优先于任何计划日期",
            "account_operation",
            "一个推荐动作",
            "不得在一个输出中并行执行多个路由",
        ),
    ),
    "cold.actual_send_dates": (
        "cold",
        (
            "第 5 个工作日",
            "第 7 个工作日",
            "actual_sent_at",
            "草稿日、批准日、计划日和建议日都不能作为实发基准",
            "缺少上一封实际发送记录时，不得计算",
        ),
    ),
    "cold.first_touch_exception": (
        "cold",
        (
            "email_channel_gap_packet",
            "继续研究可正常使用的邮箱",
            "明确批准一个合格的其他渠道首次触达例外",
            "经业务员明确批准的其他渠道首次触达例外实际发送后仍无回复",
            "另行逐项批准一个明确的下一受控动作",
            "关闭当前触达",
            "不得增加、合并、重命名或扩展选项",
        ),
    ),
    "cold.alternate_channel": (
        "cold",
        (
            "路径 A",
            "路径 B",
            "渠道证据不足",
            "只推荐一个其他渠道",
            "只准备一次返回邮件",
            "LinkedIn、WhatsApp 和电话材料必须分别重写",
        ),
    ),
    "cold.regular_and_event_cadence": (
        "cold",
        (
            "cadence_decision_packet",
            "initial_email_sequence_completed",
            "alternate_channel_step_completed",
            "return_email_actually_sent",
            "regular_cadence_anchor",
            "unadjusted_next_date",
            "recommended_next_date",
            "event_touch_candidate",
            "recorded_validation_question",
            "ai_suggested_validation_question",
            "风险硬门优先于有效事件",
            "2026-08-03",
        ),
    ),
    "reply.output_and_revision": (
        "reply",
        (
            "中文回复建议",
            "客户语言邮件预稿",
            "逐意一致的中文译文",
            "自然语言修订",
            "继承完整线程",
            "只否定预稿但不给方向",
        ),
    ),
    "reply.evidence_and_question": (
        "reply_evidence",
        (
            "客户主张不自动变成公司事实",
            "AI 推断不得作为对外事实",
            "禁止猜测数字",
            "一个关键问题只能索取一个缺失事实",
            "日期未提供",
            "未使用的资料不得包装成依据",
        ),
    ),
    "reply.special_handling": (
        "special",
        (
            "时间线",
            "两至三种可选策略",
            "不得承认责任",
            "不得放弃合同权利",
            "未经公司责任人明确批准",
            "不得编造事故原因",
            "仍只为最终推荐策略提供一份对外预稿",
        ),
    ),
    "workbook.draft_and_normalization": (
        "workbook",
        (
            "content_status = 草稿",
            "actual_sent_at = 空",
            "10:00",
            "due_record",
            "date_basis_touch_id",
            "date_basis_actual_sent_at",
            "new_value_or_question",
            "一天一条审核任务",
            "只写草稿字段",
            "重新计算第 5 个工作日、第 7 个工作日或 10 个自然日",
        ),
    ),
    "workbook.archive_and_isolation": (
        "workbook",
        (
            "只有实际收件、实际发件及实际附件",
            "不同公司使用不同稳定 `company_id` 和数据根目录",
            "公开插件只包含空白模板",
        ),
    ),
    "automation.disabled_and_review_only": (
        "config",
        (
            '"workday_check_time": "10:00"',
            '"activation_state": "disabled_until_named_workbook_and_standing_authorization"',
            '"review_task_mode": "one_task_per_workday"',
            '"open_review_task": true',
            '"standing_draft_write_authorized": false',
            '"actual_sent_at"',
        ),
    ),
    "compatibility.single_owner": (
        "legacy",
        (
            "standalone compatibility email workflow",
            "do not run both skills on the same reply task",
        ),
    ),
    "readme.optional_compatibility": (
        "readme",
        (
            "optional compatibility plugin",
            "Do not run it alongside `foreign-trade-customer-operations` for the same reply",
        ),
    ),
}


FORBIDDEN: dict[str, tuple[str, tuple[str, ...]]] = {
    "skill.no_send_or_research": (
        "skill",
        (
            "automatically sends",
            "research new prospects and prepare the reply",
            "choose development priority for the salesperson",
        ),
    ),
    "cold.no_draft_anchor_or_event_reset": (
        "cold",
        (
            "可以用草稿日作为实发基准",
            "事件触达可以重置 regular_cadence_anchor",
            "可以同日多渠道复制发送",
        ),
    ),
    "reply.no_fact_invention": (
        "reply_evidence",
        ("可以猜测价格", "客户主张自动变成公司事实"),
    ),
}


def frontmatter_keys(text: str) -> list[str]:
    if not text.startswith("---\n"):
        return []
    parts = text.split("---", 2)
    if len(parts) < 3:
        return []
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
    for label, (text_key, fragments) in FORBIDDEN.items():
        present = [fragment for fragment in fragments if fragment in texts[text_key]]
        if present:
            diagnostics.append(f"{label}: forbidden {present!r}")
    if frontmatter_keys(texts["skill"]) != ["name", "description"]:
        diagnostics.append(
            "skill.frontmatter: expected exactly name and description in that order"
        )
    for key in ("manifest", "config"):
        try:
            parsed = json.loads(texts[key])
        except json.JSONDecodeError as exc:
            diagnostics.append(f"{key}.json: invalid JSON: {exc}")
            continue
        if key == "manifest" and parsed.get("name") != "foreign-trade-customer-operations":
            diagnostics.append("manifest.name: unexpected plugin name")
    return diagnostics


def validator_self_check() -> list[str]:
    failures: list[str] = []
    for label, (text_key, fragments) in RULES.items():
        for fragment in fragments:
            mutated = dict(TEXTS)
            mutated[text_key] = mutated[text_key].replace(fragment, "")
            if not any(
                item.startswith(label + ":") for item in diagnostics_for(mutated)
            ):
                failures.append(f"{label}: validator accepted removal of {fragment!r}")
    for label, (text_key, fragments) in FORBIDDEN.items():
        mutated = dict(TEXTS)
        mutated[text_key] += "\n" + fragments[0]
        if not any(item.startswith(label + ":") for item in diagnostics_for(mutated)):
            failures.append(f"{label}: validator accepted forbidden wording")
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
        print(f"FAIL: {len(diagnostics)} customer-operations contract diagnostics")
        return 1
    print(
        "PASS: customer-operations routing, cold sequence, channel gates, cadence, "
        "reply, serious-issue, workbook, automation, and compatibility contracts are present"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
