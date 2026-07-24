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

FULL_DD_GATE_TERMS = [
    "salesperson_classification = 潜力客户",
    "明确启动完整背调",
    "两个条件同时满足",
    "普通候选",
    "不得启动完整背调",
]

ROUTING_DESCRIPTION_TERMS = [
    "pre-reply or unanswered prospect-development outreach",
    "received customer replies",
    "foreign-trade-email-assistant",
]

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


def main() -> int:
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

    require_terms(
        diagnostics,
        "research.full_due_diligence_dual_gate",
        references["research"],
        FULL_DD_GATE_TERMS,
    )

    skill_description = frontmatter_description(skill_text)
    if not skill_description:
        diagnostics.append("skill.routing_description: missing frontmatter description")
    else:
        require_terms(
            diagnostics,
            "skill.routing_description",
            skill_description,
            ROUTING_DESCRIPTION_TERMS,
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
