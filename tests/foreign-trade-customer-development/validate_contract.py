"""Static ownership and evidence contracts for customer development.

The validator intentionally checks hard boundaries and required output shapes.
It does not claim that live research behavior has been forward-tested.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
PLUGIN_ROOT = ROOT / "plugins" / "foreign-trade-customer-development"
SKILL_ROOT = PLUGIN_ROOT / "skills" / "foreign-trade-customer-development"


def read(relative: str) -> str:
    return (SKILL_ROOT / relative).read_text(encoding="utf-8")


TEXTS = {
    "skill": read("SKILL.md"),
    "research": read("references/research-and-sources.md"),
    "evidence": read("references/evidence-contacts-and-risk.md"),
    "opportunity": read("references/opportunity-and-outreach.md"),
    "workbook": read("references/workbook-and-handoff.md"),
    "agent": read("agents/openai.yaml"),
    "manifest": (PLUGIN_ROOT / ".codex-plugin" / "plugin.json").read_text(
        encoding="utf-8"
    ),
    "readme": (ROOT / "README.md").read_text(encoding="utf-8"),
}


RULES: dict[str, tuple[str, tuple[str, ...]]] = {
    "skill.routes_and_stops": (
        "skill",
        (
            "route_portfolio_review",
            "direction_compilation",
            "direction_discovery",
            "direction_validation",
            "candidate_scan",
            "direction_review",
            "full_due_diligence",
            "outreach_handoff",
            "reply_handoff",
            "never writes an external email",
            "never writes a communication draft",
        ),
    ),
    "skill.salesperson_authority": (
        "skill",
        (
            "target selection",
            "customer value",
            "priority",
            "final product decision",
            "contact approval",
            "every external message",
        ),
    ),
    "research.route_led_formula": (
        "research",
        (
            "company_route_pool_packet",
            "source_route_candidate_id",
            "direction_derivation_chain",
            "approved_product_fact",
            "effect_or_function_boundary",
            "application_conditions",
            "observable_product_signal",
            "target_enterprise_rule",
            "candidate_direct_evidence_rule",
            "counterevidence_or_unknown",
            "事实、推断和未知",
            "不得借助常识跨越",
        ),
    ),
    "research.route_review_and_readiness": (
        "research",
        (
            "route_portfolio_review_packet",
            "producer_registry_reference",
            "route_packet_sha256",
            "development_readiness_request",
            "development_readiness_view",
            "next_owner: company-product-knowledge-builder",
            "commercial_readiness_status",
            "不得反写 map_route_status",
            "不得生成综合路线评分",
            "国家或地区假设不得直接变成最终市场优先级",
        ),
    ),
    "research.direction_lifecycle": (
        "research",
        (
            "direction_status = 已确认可扫描",
            "不得偷偷启动候选池",
            "direction_feedback_packet",
            "reviewed_scan_runs",
            "保留／调整／暂缓／淘汰",
            "不得自动改写 direction_status",
            "不得用候选数量给方向排名",
        ),
    ),
    "research.candidate_scope_and_gate": (
        "research",
        (
            "全部合格候选公司",
            "不设固定数量上限",
            "公司或品牌特定的直接产品证据",
            "不放入候选池",
            "不得为候选池打分、排序",
            "不能仅凭外观、行业惯例或“可能需要”",
        ),
    ),
    "research.sources_and_customs": (
        "research",
        (
            "公开可访问的来源是默认范围",
            "登录、订阅或付费来源",
            "不得索取、记录、复制或保存密码",
            "来源发布日期（未知则写未知）",
            "不得将数据源中的可见记录称为公司全部贸易",
            "不得由货运票数",
        ),
    ),
    "research.full_due_diligence": (
        "research",
        (
            "salesperson_classification = 潜力客户",
            "业务员明确启动完整背调",
            "现有供应方向",
            "合作障碍",
            "替代机会",
            "当前产品机会",
            "未来新品机会",
            "长期关注主题",
            "持续触达理由",
        ),
    ),
    "evidence.contact_and_risk": (
        "evidence",
        (
            "联系信息来源",
            "真实性",
            "来源可靠性",
            "使用权限",
            "限制使用",
            "隔离待核实",
            "逐项批准",
            "暂停待业务员审核",
            "风险硬门优先于有效事件",
        ),
    ),
    "opportunity.project_and_handoff": (
        "opportunity",
        (
            "project_recommendation",
            "内部比较三个**项目方案**",
            "development_direction",
            "outreach_handoff_packet",
            "allowed_claims",
            "prohibited_claims",
            "outreach_scope",
            "不再准备首封邮件",
            "foreign-trade-customer-operations",
        ),
    ),
    "workbook.mapping_and_handoff": (
        "workbook",
        (
            "第 1 行是机器字段名",
            "第 2 行是业务可读的中文字段说明",
            "direction_derivation_chain",
            "route_review_id",
            "source_route_review_id",
            "direction_feedback_packet",
            "未合格或待核实公司不伪装成客户记录",
            "客户经营与沟通移交",
            "target_skill 固定为 foreign-trade-customer-operations",
            "业务员明确指定字段及新值",
            "写入后必须重新打开验证",
            "重新打开时核对工作表、编号、变更单元格和保存后的值",
            "response_reference",
            "sender_identity_status",
            "confirmed_context",
            "actual_send_history",
            "salesperson_request",
        ),
    ),
    "interfaces.direction_first": (
        "manifest",
        (
            "业务员选定路线的开发方向编译",
            "不代写、不发送，不代替业务员做最终商业判断",
            "校验已登记的公司路线候选池交接包",
        ),
    ),
    "readme.boundary": (
        "readme",
        (
            "returns all qualified candidate companies in the declared scope",
            "prepares an evidence-bound communication handoff without drafting",
            "foreign-trade-customer-operations",
        ),
    ),
}


FORBIDDEN: dict[str, tuple[str, tuple[str, ...]]] = {
    "research.no_fixed_cap_or_ai_priority": (
        "research",
        (
            "每轮20个候选客户",
            "Top 20 immediately",
            "AI 自动选择开发优先级",
        ),
    ),
    "workbook.no_stale_handoff_owner": (
        "workbook",
        ("## 邮件助手移交", "target_skill 固定为 foreign-trade-email-assistant"),
    ),
    "opportunity.no_external_draft": (
        "opportunity",
        ("本技能准备首封邮件", "本技能生成开发信正文"),
    ),
}


def frontmatter_keys(text: str) -> list[str]:
    if not text.startswith("---\n"):
        return []
    parts = text.split("---", 2)
    if len(parts) < 3:
        return []
    keys = []
    for line in parts[1].splitlines():
        if line and not line.startswith((" ", "\t")) and ":" in line:
            keys.append(line.split(":", 1)[0].strip())
    return keys


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
    try:
        manifest = json.loads(texts["manifest"])
    except json.JSONDecodeError as exc:
        diagnostics.append(f"manifest.json: invalid JSON: {exc}")
    else:
        if manifest.get("name") != "foreign-trade-customer-development":
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
        print(f"FAIL: {len(diagnostics)} customer-development contract diagnostics")
        return 1
    print(
        "PASS: customer-development direction formula, lifecycle, evidence, "
        "candidate, due-diligence, workbook, and handoff contracts are present"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
