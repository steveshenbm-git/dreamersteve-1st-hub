from pathlib import Path
import re
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
REFERENCE_ROOT = (
    REPO_ROOT
    / "plugins"
    / "foreign-trade-customer-development"
    / "skills"
    / "foreign-trade-customer-development"
    / "references"
)
SKILL_PATH = REFERENCE_ROOT.parent / "SKILL.md"

REQUIRED_RESEARCH_TERMS = {
    "public_default": ["公开可访问的来源是默认范围", "不得要求业务员授权公开来源"],
    "social_identity": ["官网外链", "平台认证", "跨平台互链", "主体信息一致性", "疑似官方"],
    "company_scale": ["公开财务", "员工规模", "办公或生产设施", "市场覆盖", "销售渠道", "经营活动"],
    "full_due_diligence": ["现有供应方向", "合作障碍", "替代机会", "长期关注主题", "持续触达理由", "未来新品机会", "监管公告"],
}

REQUIRED_RISK_TERMS = ["付款", "信用", "交易身份", "暂停待业务员审核"]
REQUIRED_RELIABILITY_TERMS = ["支持证据", "反对或冲突证据", "剩余缺口"]
REQUIRED_OPPORTUNITY_TERMS = ["舍弃其他方向的简要原因", "不得直接复制完整邮件", "渠道长度", "行动请求"]
REQUIRED_WORKBOOK_FIELDS = {
    "联系人": ["employer_or_entity", "entity_match_basis", "contact_source_reference", "uncertainty_note"],
    "证据来源": ["source_region_or_jurisdiction"],
}

FULL_DD_CANONICAL_CLAUSE = (
    "只有当 salesperson_classification = 潜力客户 与 业务员明确启动完整背调 "
    "两个条件同时满足时，才允许 research_level = full_due_diligence；"
    "普通候选不得启动完整背调。"
)
ROUTING_CANONICAL_CLAUSE = (
    "This skill is limited to pre-reply or unanswered prospect-development outreach; "
    "received customer replies are excluded and routed to foreign-trade-email-assistant."
)

EMAIL_GAP_CANONICAL_CLAUSE = (
    "没有可正常使用的邮箱时，不得由 AI 自动把其他渠道作为首次触达；"
    "必须先记录邮件渠道缺口并等待业务员决定。"
)
INBOUND_EVIDENCE_CANONICAL_CLAUSE = (
    "未核验发件人身份或邮件头的入站邮件不得标为官方直接证据；"
    "无论证据状态如何，回复硬停和邮件助手移交始终优先。"
)
EVENT_TOUCH_CANONICAL_CLAUSE = (
    "发现有效事件时，AI 必须准备一份待业务员审核的额外触达候选材料；"
    "不得自动发送，且事件触达不得重置 regular_cadence_anchor。"
)

FULL_DD_OPPOSITE_COUNTEREXAMPLE = (
    "salesperson_classification = 潜力客户 与业务员明确启动完整背调并非必须同时满足，"
    "任一条件即可。普通候选不得启动完整背调。"
)
ROUTING_OPPOSITE_COUNTEREXAMPLE = (
    "Received customer replies are not handled outside this skill and route here before "
    "foreign-trade-email-assistant."
)
EMAIL_GAP_OPPOSITE_COUNTEREXAMPLE = (
    "没有可正常使用的邮箱时，AI 可自动把其他渠道作为首次触达，"
    "无需等待业务员决定。"
)
INBOUND_EVIDENCE_OPPOSITE_COUNTEREXAMPLE = (
    "未核验发件人身份或邮件头的入站邮件仍可标为官方直接证据。"
)
INBOUND_HANDOFF_DELAY_OPPOSITE_COUNTEREXAMPLE = (
    "只有保存真实回复和发送历史后，才可准备 email_assistant_handoff"
)
INBOUND_IDENTITY_DELAY_OPPOSITE_COUNTEREXAMPLE = (
    "必须先核验发件人身份或邮件头，之后才可移交 foreign-trade-email-assistant。"
)
EVENT_TOUCH_OPPOSITE_COUNTEREXAMPLE = (
    "发现有效事件时，AI 可不准备额外触达候选材料，"
    "也可自动发送并重置 regular_cadence_anchor。"
)

REFERENCE_FILES = {
    "research": REFERENCE_ROOT / "research-and-sources.md",
    "evidence": REFERENCE_ROOT / "evidence-contacts-and-risk.md",
    "opportunity": REFERENCE_ROOT / "opportunity-and-outreach.md",
    "workbook": REFERENCE_ROOT / "workbook-and-handoff.md",
}


def load_references() -> dict[str, str]:
    loaded = {}
    for name, path in REFERENCE_FILES.items():
        try:
            loaded[name] = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            print(f"FAIL reference_file.{name}: cannot read UTF-8 file {path}: {exc}")
            sys.exit(2)
    return loaded


def load_skill() -> str:
    try:
        return SKILL_PATH.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        print(f"FAIL skill_file: cannot read UTF-8 file {SKILL_PATH}: {exc}")
        sys.exit(2)


def frontmatter_description(text: str) -> str:
    match = re.search(
        r"\A---\s*$\n.*?^description:\s*(.+?)\s*$\n.*?^---\s*$",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    return match.group(1).strip() if match else ""


def require_terms(
    diagnostics: list[str],
    contract: str,
    text: str,
    terms: list[str],
) -> None:
    missing = [term for term in terms if term not in text]
    if missing:
        diagnostics.append(f"{contract}: missing {', '.join(repr(term) for term in missing)}")


def markdown_section(text: str, heading: str) -> str:
    match = re.search(
        rf"^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    return match.group(1) if match else ""


def normalize_contract_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("`", "")).strip()


def has_uncontradicted_canonical_clause(
    text: str,
    canonical_clause: str,
    opposite_clauses: list[str],
) -> bool:
    normalized_text = normalize_contract_text(text)
    if normalize_contract_text(canonical_clause) not in normalized_text:
        return False
    return not any(
        normalize_contract_text(opposite_clause) in normalized_text
        for opposite_clause in opposite_clauses
    )


def has_full_dd_dual_gate(text: str) -> bool:
    return has_uncontradicted_canonical_clause(
        text,
        FULL_DD_CANONICAL_CLAUSE,
        [FULL_DD_OPPOSITE_COUNTEREXAMPLE],
    )


def has_routing_description_contract(text: str) -> bool:
    return has_uncontradicted_canonical_clause(
        text,
        ROUTING_CANONICAL_CLAUSE,
        [ROUTING_OPPOSITE_COUNTEREXAMPLE],
    )


def has_email_gap_contract(text: str) -> bool:
    return has_uncontradicted_canonical_clause(
        text,
        EMAIL_GAP_CANONICAL_CLAUSE,
        [EMAIL_GAP_OPPOSITE_COUNTEREXAMPLE],
    )


def has_inbound_evidence_contract(text: str) -> bool:
    return has_uncontradicted_canonical_clause(
        text,
        INBOUND_EVIDENCE_CANONICAL_CLAUSE,
        [
            INBOUND_EVIDENCE_OPPOSITE_COUNTEREXAMPLE,
            INBOUND_HANDOFF_DELAY_OPPOSITE_COUNTEREXAMPLE,
            INBOUND_IDENTITY_DELAY_OPPOSITE_COUNTEREXAMPLE,
        ],
    )


def has_event_touch_contract(text: str) -> bool:
    return has_uncontradicted_canonical_clause(
        text,
        EVENT_TOUCH_CANONICAL_CLAUSE,
        [EVENT_TOUCH_OPPOSITE_COUNTEREXAMPLE],
    )


def contract_matcher_self_check() -> list[str]:
    failures = []
    if not has_full_dd_dual_gate(FULL_DD_CANONICAL_CLAUSE):
        failures.append("full-DD canonical clause was rejected")
    if has_full_dd_dual_gate(FULL_DD_OPPOSITE_COUNTEREXAMPLE):
        failures.append("full-DD opposite counterexample was accepted")
    if has_full_dd_dual_gate(
        FULL_DD_CANONICAL_CLAUSE + "\n" + FULL_DD_OPPOSITE_COUNTEREXAMPLE
    ):
        failures.append("full-DD canonical-plus-opposite counterexample was accepted")
    if not has_routing_description_contract(ROUTING_CANONICAL_CLAUSE):
        failures.append("routing canonical clause was rejected")
    if has_routing_description_contract(ROUTING_OPPOSITE_COUNTEREXAMPLE):
        failures.append("routing opposite counterexample was accepted")
    if has_routing_description_contract(
        ROUTING_CANONICAL_CLAUSE + "\n" + ROUTING_OPPOSITE_COUNTEREXAMPLE
    ):
        failures.append("routing canonical-plus-opposite counterexample was accepted")

    new_contracts = [
        (
            "email-gap",
            has_email_gap_contract,
            EMAIL_GAP_CANONICAL_CLAUSE,
            [EMAIL_GAP_OPPOSITE_COUNTEREXAMPLE],
        ),
        (
            "inbound-evidence",
            has_inbound_evidence_contract,
            INBOUND_EVIDENCE_CANONICAL_CLAUSE,
            [
                INBOUND_EVIDENCE_OPPOSITE_COUNTEREXAMPLE,
                INBOUND_HANDOFF_DELAY_OPPOSITE_COUNTEREXAMPLE,
                INBOUND_IDENTITY_DELAY_OPPOSITE_COUNTEREXAMPLE,
            ],
        ),
        (
            "event-touch",
            has_event_touch_contract,
            EVENT_TOUCH_CANONICAL_CLAUSE,
            [EVENT_TOUCH_OPPOSITE_COUNTEREXAMPLE],
        ),
    ]
    for name, matcher, canonical, opposites in new_contracts:
        if not matcher(canonical):
            failures.append(f"{name} canonical clause was rejected")
        for opposite in opposites:
            if matcher(opposite):
                failures.append(f"{name} opposite counterexample was accepted")
            if matcher(canonical + "\n" + opposite):
                failures.append(
                    f"{name} canonical-plus-opposite counterexample was accepted"
                )
    return failures


def main() -> int:
    self_check_failures = contract_matcher_self_check()
    if self_check_failures:
        for failure in self_check_failures:
            print(f"FAIL validator.self_check: {failure}")
        print(f"FAIL: {len(self_check_failures)} validator self-check diagnostics")
        return 2

    references = load_references()
    skill_text = load_skill()
    diagnostics: list[str] = []

    for contract, terms in REQUIRED_RESEARCH_TERMS.items():
        require_terms(
            diagnostics,
            f"research.{contract}",
            references["research"],
            terms,
        )

    if not has_full_dd_dual_gate(references["research"]):
        diagnostics.append(
            "research.full_due_diligence_dual_gate: missing canonical dual-gate clause"
        )

    skill_description = frontmatter_description(skill_text)
    if not skill_description:
        diagnostics.append("skill.routing_description: missing frontmatter description")
    else:
        if not has_routing_description_contract(skill_description):
            diagnostics.append(
                "skill.routing_description: missing canonical received-reply exclusion "
                "and email-assistant routing clause"
            )

    require_terms(
        diagnostics,
        "evidence.risk_hard_gate",
        markdown_section(references["evidence"], "风险硬门"),
        REQUIRED_RISK_TERMS,
    )
    require_terms(
        diagnostics,
        "evidence.reliability_output",
        markdown_section(references["evidence"], "公司资料可靠性"),
        REQUIRED_RELIABILITY_TERMS,
    )
    require_terms(
        diagnostics,
        "opportunity.output_and_channel",
        references["opportunity"],
        REQUIRED_OPPORTUNITY_TERMS,
    )

    if not has_email_gap_contract(references["opportunity"]):
        diagnostics.append(
            "opportunity.email_gap_first_touch: missing canonical no-email "
            "salesperson-decision clause"
        )

    inbound_contract_text = "\n".join(
        [
            references["evidence"],
            references["workbook"],
            references["opportunity"],
        ]
    )
    if not has_inbound_evidence_contract(inbound_contract_text):
        diagnostics.append(
            "evidence.unverified_inbound_email: missing canonical inbound-evidence "
            "and immediate reply-handoff clause, or a conflicting delayed-handoff "
            "clause is present"
        )

    if not has_event_touch_contract(references["opportunity"]):
        diagnostics.append(
            "opportunity.valid_event_candidate: missing canonical mandatory-candidate, "
            "no-auto-send, and no-anchor-reset clause"
        )

    workbook_text = references["workbook"]
    for sheet, fields in REQUIRED_WORKBOOK_FIELDS.items():
        header_match = re.search(
            rf"^{re.escape(sheet)}:\s*(.+)$",
            workbook_text,
            flags=re.MULTILINE,
        )
        declared_fields = header_match.group(1) if header_match else ""
        require_terms(
            diagnostics,
            f"workbook.fields.{sheet}",
            declared_fields,
            fields,
        )

    ownership_text = workbook_text
    ownership_requirements = [
        (
            r"业务员(?:自有|负责|已确认)[^。\n]{0,40}字段",
            "salesperson-owned or salesperson-confirmed fields",
        ),
        (r"默认(?:保留|不覆盖)", "default-preservation rule"),
        (
            r"明确(?:指定|点名|授权)[^。\n]{0,30}字段[^。\n]{0,30}新值",
            "field-specific authorization naming the field and new value",
        ),
        (r"workbook_update_packet", "authorization recorded in workbook_update_packet"),
    ]
    missing_ownership = [
        description
        for pattern, description in ownership_requirements
        if re.search(pattern, ownership_text, flags=re.DOTALL) is None
    ]
    if missing_ownership:
        diagnostics.append(
            "workbook.salesperson_field_preservation: missing "
            + "; ".join(missing_ownership)
        )

    if diagnostics:
        for diagnostic in diagnostics:
            print(f"FAIL {diagnostic}")
        print(f"FAIL: {len(diagnostics)} contract diagnostics")
        return 1

    print("PASS: all specification-traceability contracts are present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
