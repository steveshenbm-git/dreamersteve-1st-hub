from pathlib import Path
import sys
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

EXPECTED = {
    "客户总览": ["customer_id", "company_name", "legal_name", "website", "country", "business_model", "screening_status", "salesperson_classification", "information_reliability", "risk_gate", "recommended_opportunity_id", "primary_contact_id", "last_research_date", "last_touch_date", "next_action", "next_action_date", "handoff_status", "salesperson_notes"],
    "公司研究": ["research_id", "customer_id", "research_level", "section", "finding_original", "finding_zh_summary", "evidence_id", "evidence_state", "source_published_at", "observed_at", "gap_or_conflict", "salesperson_confirmed"],
    "项目机会": ["opportunity_id", "customer_id", "customer_fact", "application_or_purchase_scenario", "approved_product_reference", "fit_basis", "validation_question", "primary_contact_id", "recommendation_state", "salesperson_decision", "decision_date"],
    "联系人": ["contact_id", "customer_id", "name", "title", "possible_role", "role_evidence_id", "channel", "contact_value", "authenticity_state", "source_reliability", "usage_permission", "contact_order", "ordering_basis", "observed_at", "salesperson_approval"],
    "证据来源": ["evidence_id", "customer_id", "source_type", "source_title", "source_url_or_local_reference", "source_owner", "source_language", "original_excerpt", "zh_summary", "published_at", "observed_at", "evidence_state", "access_scope", "conflict_note"],
    "海关与贸易": ["trade_record_id", "customer_id", "data_source", "access_scope", "coverage_country", "coverage_period", "observed_entity_name", "observed_entity_address", "entity_match_basis", "trade_direction", "shipment_period", "visible_frequency", "product_description", "hs_code", "quantity", "quantity_unit", "weight", "weight_unit", "declared_value", "declared_currency", "partner_or_country", "limitation_note", "observed_at", "evidence_id"],
    "风险核验": ["risk_id", "customer_id", "risk_type", "matched_entity", "match_basis", "allegation_or_record", "evidence_id", "jurisdiction", "record_date", "observed_at", "evidence_state", "false_match_risk", "gate_status", "reviewer_decision", "decision_date"],
    "触达记录": ["touch_id", "customer_id", "contact_id", "channel", "touch_stage", "content_status", "planned_date", "actual_sent_at", "actual_content_or_local_reference", "response_state", "response_at", "next_action", "next_action_date", "salesperson_approved"],
    "移交记录": ["handoff_id", "customer_id", "trigger_channel", "trigger_touch_id", "response_reference", "development_snapshot_reference", "open_questions", "risk_gate_status", "target_skill", "handoff_status", "salesperson_decision", "decision_date"],
}

EXPECTED_ZH = {
    "客户总览": ["客户编号", "公司常用名称", "法定注册名称", "公司网站", "国家或地区", "商业模式", "筛选状态", "业务员客户分类", "信息可靠性", "风险门状态", "推荐机会编号", "主要联系人编号", "最近研究日期", "最近触达日期", "下一步行动", "下一步行动日期", "移交状态", "业务员备注"],
    "公司研究": ["研究记录编号", "客户编号", "研究层级", "研究章节", "原文研究发现", "研究发现中文摘要", "证据编号", "证据状态", "来源发布日期", "观察记录时间", "信息缺口或冲突", "业务员确认状态"],
    "项目机会": ["机会编号", "客户编号", "已确认客户事实", "应用或采购场景", "已批准产品引用", "匹配依据", "待验证问题", "主要联系人编号", "推荐状态", "业务员决定", "决定日期"],
    "联系人": ["联系人编号", "客户编号", "联系人姓名", "职务名称", "可能承担的角色", "角色证据编号", "联系渠道", "联系方式内容", "真实性状态", "来源可靠性", "使用许可", "联系顺序", "排序依据", "观察记录时间", "业务员批准状态"],
    "证据来源": ["证据编号", "客户编号", "来源类型", "来源标题", "来源网址或本地引用", "来源主体", "来源语言", "原文摘录", "中文摘要", "来源发布日期", "观察记录时间", "证据状态", "访问范围", "冲突说明"],
    "海关与贸易": ["贸易记录编号", "客户编号", "数据来源", "访问范围", "覆盖国家或地区", "覆盖期间", "观察到的企业名称", "观察到的企业地址", "主体匹配依据", "贸易方向", "货运期间", "可见交易频次", "产品描述", "海关编码", "数量", "数量单位", "重量", "重量单位", "申报价值", "申报币种", "贸易伙伴或国家", "数据局限说明", "观察记录时间", "证据编号"],
    "风险核验": ["风险记录编号", "客户编号", "风险类型", "匹配到的主体", "主体匹配依据", "指控或记录内容", "证据编号", "管辖地区", "记录日期", "观察记录时间", "证据状态", "误匹配风险", "风险门状态", "审核人决定", "决定日期"],
    "触达记录": ["触达记录编号", "客户编号", "联系人编号", "触达渠道", "触达阶段", "内容状态", "计划日期", "实际发送时间", "实发内容或本地引用", "回复状态", "回复时间", "下一步行动", "下一步行动日期", "业务员批准状态"],
    "移交记录": ["移交记录编号", "客户编号", "触发渠道", "触发触达记录编号", "回复内容引用", "客户开发快照引用", "未解决问题", "风险门状态", "目标技能", "移交状态", "业务员决定", "决定日期"],
}

path = Path(sys.argv[1])
workbook = load_workbook(path, data_only=False)
assert workbook.sheetnames == list(EXPECTED), workbook.sheetnames

for name, expected_headers in EXPECTED.items():
    sheet = workbook[name]
    headers = [cell.value for cell in sheet[1]]
    zh_headers = [cell.value for cell in sheet[2]]
    assert headers == expected_headers, f"{name}: {headers}"
    assert zh_headers == EXPECTED_ZH[name], f"{name}: {zh_headers}"
    assert sheet.freeze_panes == "A3", f"{name}: freeze_panes"
    assert sheet.auto_filter.ref == f"A2:{get_column_letter(len(expected_headers))}2", f"{name}: auto_filter"
    assert sheet.max_row == 2, f"{name}: workbook must contain no real rows from row 3"

print("PASS: workbook structure, empty-data boundary, freeze panes, and filters")
