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
PLUGIN_MANIFEST_PATH = REFERENCE_ROOT.parents[2] / ".codex-plugin" / "plugin.json"
OPENAI_AGENT_PATH = REFERENCE_ROOT.parent / "agents" / "openai.yaml"
DESIGN_PATH = (
    REPO_ROOT
    / "docs"
    / "superpowers"
    / "specs"
    / "2026-07-23-foreign-trade-customer-development-design.md"
)

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
SKILL_OUTPUT_BY_LEVEL_CANONICAL_CLAUSE = (
    "输出必须按 research_level 分流：candidate_scan 只输出候选池或候选初查并停止；"
    "full_due_diligence 才可输出一个最终项目推荐或明确证据不足结论。"
)
DESIGN_SELECTION_GATE_CANONICAL_CLAUSE = (
    "业务员从候选池中选择公司，只表示进入 candidate_scan；"
    "选择公司不等于 salesperson_classification = 潜力客户，也不等于业务员明确启动完整背调，"
    "未同时满足这两个条件不得进入 full_due_diligence。"
)
DESIGN_EVENT_INDEPENDENCE_CANONICAL_CLAUSE = (
    "有效事件候选不得因临近常规触达日期而延迟、省略或并入常规触达；"
    "事件触达独立准备、独立记录，且不重置 regular_cadence_anchor。"
)
SKILL_RESEARCH_AND_OUTREACH_ROUTE_CANONICAL_CLAUSE = (
    "research_level 只允许 candidate_scan 和 full_due_diligence 两个值；"
    "收到或疑似收到入站回复不设置第三个 research_level，"
    "而是立即停止客户开发并路由到 email_assistant_handoff。"
    "业务员已选择公司、记录 salesperson_classification = 普通候选 "
    "并明确请求准备触达后，AI 进入独立 outreach_task；"
    "该路线不启动 full_due_diligence，也不受 candidate_scan 停止规则继续阻断。"
)
DESIGN_ORDINARY_OUTREACH_GATE_CANONICAL_CLAUSE = (
    "salesperson_classification = 潜力客户 与业务员明确启动完整背调"
    "这两个条件只控制是否进入 full_due_diligence；"
    "不得用任一门槛缺失来阻止普通候选按业务员明确指令准备有限触达。"
    "业务员已选择公司、记录 salesperson_classification = 普通候选 "
    "并明确请求准备触达后，AI 进入独立 outreach_task；"
    "该路线不启动 full_due_diligence。"
)
INTERFACE_PLUGIN_DEFAULT_PROMPT_CANONICAL_CLAUSE = (
    "Run a candidate scan for this named prospect, return evidence-bound initial findings, "
    "and stop for salesperson screening. Prepare a final development recommendation only "
    "after salesperson_classification = 潜力客户 and the salesperson explicitly "
    "starts full_due_diligence."
)
INTERFACE_AGENT_DEFAULT_PROMPT_CANONICAL_CLAUSE = (
    "使用 $foreign-trade-customer-development 对这家指定客户执行 candidate_scan，"
    "整理带证据的候选初查结果，并停止等待业务员筛选。"
    "只有记录 salesperson_classification = 潜力客户 且业务员明确启动 "
    "full_due_diligence 后，才准备最终项目推荐。"
)
INTERFACE_DEFAULT_PROMPT_CANONICAL_CLAUSE = (
    INTERFACE_PLUGIN_DEFAULT_PROMPT_CANONICAL_CLAUSE
    + "\n"
    + INTERFACE_AGENT_DEFAULT_PROMPT_CANONICAL_CLAUSE
)
FINAL_RECOMMENDATION_SCOPE_CANONICAL_CLAUSE = (
    "final_recommendation 只允许在 research_level = full_due_diligence "
    "且完整背调双门槛通过后生成；candidate_scan 和 outreach_task "
    "都不得生成最终项目推荐。outreach_task 只基于已有候选初查证据、"
    "已批准产品事实和可用联系证据准备有限触达材料。"
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
SKILL_OUTPUT_BY_LEVEL_OPPOSITE_COUNTEREXAMPLES = [
    (
        "Return Chinese analysis, one final recommendation or an explicit "
        "evidence-insufficient conclusion, source/date/evidence labels, salesperson "
        "decisions still required, and a verified workbook update status."
    ),
    (
        "输出必须按 research_level 分流：candidate_scan 可以输出一个最终项目推荐；"
        "full_due_diligence 再补充更详细的推荐。"
    ),
    (
        "candidate_scan 可直接选定最终客户并输出最终项目，"
        "无需等待 full_due_diligence。"
    ),
    "无论 research_level 为何，都输出一个最终项目推荐。",
]
DESIGN_SELECTION_GATE_OPPOSITE_COUNTEREXAMPLES = [
    "业务员选择后，AI才可对入选公司进行联系人识别和完整背调。",
    "业务员从候选池中选择公司后，即可进入 full_due_diligence。",
    (
        "候选公司一旦被业务员选中，自动视为 salesperson_classification = 潜力客户 "
        "且已明确启动完整背调。"
    ),
    (
        "选择公司、salesperson_classification = 潜力客户 或业务员明确启动完整背调，"
        "任一条件即足以进入 full_due_diligence。"
    ),
]
DESIGN_EVENT_INDEPENDENCE_OPPOSITE_COUNTEREXAMPLES = [
    "额外触达与固定日期过近时，可合并为一次更有价值的沟通。",
    "有效事件候选临近常规触达日期时，可延迟到常规日期再准备。",
    "有效事件候选临近常规触达日期时，可省略独立事件触达。",
    "有效事件候选可并入常规触达，无需独立准备或记录。",
    "事件触达实际发送后，应重置 regular_cadence_anchor。",
]
SKILL_RESEARCH_AND_OUTREACH_ROUTE_OPPOSITE_COUNTEREXAMPLES = [
    (
        "reply 是第三个 research_level；收到入站回复后将 "
        "research_level 设为 reply。"
    ),
    (
        "输出必须按 research_level 分流：candidate_scan、full_due_diligence "
        "与 reply 分别是三个 research_level。"
    ),
    (
        "普通候选即使已由业务员选择并明确请求准备触达，"
        "也必须停在 candidate_scan，不得进入独立 outreach_task。"
    ),
    (
        "普通候选只有升级为潜力客户并启动 full_due_diligence 后，"
        "才可准备触达。"
    ),
    "salesperson_classification = 不继续 也可进入 outreach_task。",
    (
        "潜力客户未明确启动 full_due_diligence 时，"
        "也可直接进入 outreach_task 准备触达材料。"
    ),
]
DESIGN_ORDINARY_OUTREACH_GATE_OPPOSITE_COUNTEREXAMPLES = [
    "任一条件缺失时，AI不得继续完整背调、深挖联系人或准备正式触达材料。",
    (
        "任一完整背调门槛缺失时，AI不得继续完整背调、"
        "深挖联系人或准备正式触达材料。"
    ),
    (
        "普通候选必须同时通过潜力客户分类和完整背调启动门槛，"
        "才能按业务员指令准备有限触达。"
    ),
    (
        "业务员已选择并标为普通候选的公司不存在独立触达任务路线；"
        "candidate_scan 停止规则始终优先。"
    ),
]
INTERFACE_DEFAULT_PROMPT_OPPOSITE_COUNTEREXAMPLES = [
    "Research this prospect company and prepare one evidence-bound development recommendation.",
    (
        "使用 $foreign-trade-customer-development 调查这家潜在客户，整理证据，"
        "并准备一份由业务员审核的开发建议。"
    ),
    (
        "默认指定客户入口直接要求一份最终开发推荐，"
        "不必等待潜力客户分类或业务员启动完整背调。"
    ),
]
FINAL_RECOMMENDATION_SCOPE_OPPOSITE_COUNTEREXAMPLES = [
    "无论 research_level 或 task_route 为何，都应生成 final_recommendation。",
    "outreach_task 必须内部比较三个候选方向并输出一个最终推荐。",
    "candidate_scan 可以直接生成最终项目推荐。",
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


def load_plugin_interface() -> str:
    texts = []
    for label, path in [
        ("plugin manifest", PLUGIN_MANIFEST_PATH),
        ("OpenAI agent", OPENAI_AGENT_PATH),
    ]:
        try:
            texts.append(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError) as exc:
            print(f"FAIL interface_file: cannot read UTF-8 {label} file {path}: {exc}")
            sys.exit(2)
    return "\n".join(texts)


def load_design() -> str:
    try:
        return DESIGN_PATH.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        print(f"FAIL design_file: cannot read UTF-8 file {DESIGN_PATH}: {exc}")
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


def has_skill_output_by_level_contract(text: str) -> bool:
    return has_uncontradicted_canonical_clause(
        text,
        SKILL_OUTPUT_BY_LEVEL_CANONICAL_CLAUSE,
        SKILL_OUTPUT_BY_LEVEL_OPPOSITE_COUNTEREXAMPLES,
    )


def has_design_selection_gate_contract(text: str) -> bool:
    return has_uncontradicted_canonical_clause(
        text,
        DESIGN_SELECTION_GATE_CANONICAL_CLAUSE,
        DESIGN_SELECTION_GATE_OPPOSITE_COUNTEREXAMPLES,
    )


def has_design_event_independence_contract(text: str) -> bool:
    return has_uncontradicted_canonical_clause(
        text,
        DESIGN_EVENT_INDEPENDENCE_CANONICAL_CLAUSE,
        DESIGN_EVENT_INDEPENDENCE_OPPOSITE_COUNTEREXAMPLES,
    )


def has_skill_research_and_outreach_route_contract(text: str) -> bool:
    return has_uncontradicted_canonical_clause(
        text,
        SKILL_RESEARCH_AND_OUTREACH_ROUTE_CANONICAL_CLAUSE,
        SKILL_RESEARCH_AND_OUTREACH_ROUTE_OPPOSITE_COUNTEREXAMPLES,
    )


def has_design_ordinary_outreach_gate_contract(text: str) -> bool:
    return has_uncontradicted_canonical_clause(
        text,
        DESIGN_ORDINARY_OUTREACH_GATE_CANONICAL_CLAUSE,
        DESIGN_ORDINARY_OUTREACH_GATE_OPPOSITE_COUNTEREXAMPLES,
    )


def has_interface_default_prompt_contract(text: str) -> bool:
    normalized_text = normalize_contract_text(text)
    has_both_prompts = all(
        normalize_contract_text(clause) in normalized_text
        for clause in [
            INTERFACE_PLUGIN_DEFAULT_PROMPT_CANONICAL_CLAUSE,
            INTERFACE_AGENT_DEFAULT_PROMPT_CANONICAL_CLAUSE,
        ]
    )
    has_listed_opposite = any(
        normalize_contract_text(opposite) in normalized_text
        for opposite in INTERFACE_DEFAULT_PROMPT_OPPOSITE_COUNTEREXAMPLES
    )
    return has_both_prompts and not has_listed_opposite


def has_final_recommendation_scope_contract(text: str) -> bool:
    return has_uncontradicted_canonical_clause(
        text,
        FINAL_RECOMMENDATION_SCOPE_CANONICAL_CLAUSE,
        FINAL_RECOMMENDATION_SCOPE_OPPOSITE_COUNTEREXAMPLES,
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
        (
            "skill-output-by-level",
            has_skill_output_by_level_contract,
            SKILL_OUTPUT_BY_LEVEL_CANONICAL_CLAUSE,
            SKILL_OUTPUT_BY_LEVEL_OPPOSITE_COUNTEREXAMPLES,
        ),
        (
            "design-selection-gate",
            has_design_selection_gate_contract,
            DESIGN_SELECTION_GATE_CANONICAL_CLAUSE,
            DESIGN_SELECTION_GATE_OPPOSITE_COUNTEREXAMPLES,
        ),
        (
            "design-event-independence",
            has_design_event_independence_contract,
            DESIGN_EVENT_INDEPENDENCE_CANONICAL_CLAUSE,
            DESIGN_EVENT_INDEPENDENCE_OPPOSITE_COUNTEREXAMPLES,
        ),
        (
            "skill-research-and-outreach-route",
            has_skill_research_and_outreach_route_contract,
            SKILL_RESEARCH_AND_OUTREACH_ROUTE_CANONICAL_CLAUSE,
            SKILL_RESEARCH_AND_OUTREACH_ROUTE_OPPOSITE_COUNTEREXAMPLES,
        ),
        (
            "design-ordinary-outreach-gate",
            has_design_ordinary_outreach_gate_contract,
            DESIGN_ORDINARY_OUTREACH_GATE_CANONICAL_CLAUSE,
            DESIGN_ORDINARY_OUTREACH_GATE_OPPOSITE_COUNTEREXAMPLES,
        ),
        (
            "interface-default-prompt",
            has_interface_default_prompt_contract,
            INTERFACE_DEFAULT_PROMPT_CANONICAL_CLAUSE,
            INTERFACE_DEFAULT_PROMPT_OPPOSITE_COUNTEREXAMPLES,
        ),
        (
            "final-recommendation-scope",
            has_final_recommendation_scope_contract,
            FINAL_RECOMMENDATION_SCOPE_CANONICAL_CLAUSE,
            FINAL_RECOMMENDATION_SCOPE_OPPOSITE_COUNTEREXAMPLES,
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
    plugin_interface_text = load_plugin_interface()
    design_text = load_design()
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

    if not has_skill_output_by_level_contract(skill_text):
        diagnostics.append(
            "skill.output_by_research_level: missing canonical candidate-pool versus "
            "full-due-diligence output split, or a listed opposite clause is present"
        )

    if not has_design_selection_gate_contract(design_text):
        diagnostics.append(
            "design.candidate_selection_dual_gate: missing canonical selected-company "
            "candidate-scan and full-DD dual-gate clause, or a listed opposite clause is present"
        )

    if not has_design_event_independence_contract(design_text):
        diagnostics.append(
            "design.event_touch_independence: missing canonical no-delay, no-omission, "
            "no-merge, independent-record, and no-anchor-reset clause, or a listed opposite "
            "clause is present"
        )

    if not has_skill_research_and_outreach_route_contract(
        skill_text + "\n" + references["research"]
    ):
        diagnostics.append(
            "skill.research_level_and_outreach_route: missing canonical two-value "
            "research-level, separate reply-handoff, and selected ordinary-candidate "
            "outreach-task clause, or a listed opposite clause is present"
        )

    if not has_design_ordinary_outreach_gate_contract(design_text):
        diagnostics.append(
            "design.ordinary_candidate_outreach_gate: missing canonical full-DD-only "
            "dual-gate scope and independent selected ordinary-candidate outreach-task "
            "clause, or a listed opposite clause is present"
        )

    if not has_interface_default_prompt_contract(plugin_interface_text):
        diagnostics.append(
            "interface.default_prompt_candidate_scan: missing canonical named-prospect "
            "candidate-scan-and-stop default prompt with the full-DD dual gate for final "
            "recommendations, or a listed opposite clause is present"
        )

    if not has_final_recommendation_scope_contract(references["opportunity"]):
        diagnostics.append(
            "opportunity.final_recommendation_scope: missing canonical full-DD-only "
            "final-recommendation and limited ordinary-candidate outreach-task clause, "
            "or a listed opposite clause is present"
        )

    if not has_final_recommendation_scope_contract(design_text):
        diagnostics.append(
            "design.final_recommendation_scope: missing canonical full-DD-only "
            "final-recommendation and limited ordinary-candidate outreach-task clause, "
            "or a listed opposite clause is present"
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
