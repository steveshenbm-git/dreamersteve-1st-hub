"""Select local workbook records that may receive a review-only communication draft.

This module intentionally does not write workbooks, call Codex, or send messages.
Those actions require a named local workbook and a separately approved standing
authorization. It exists so the eventual 10:00 workday automation has a
deterministic, testable eligibility gate.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Iterable
from zoneinfo import ZoneInfo


BLOCKING_RISK_STATES = {"暂停待业务员审核", "已关闭"}
BLOCKING_RESPONSE_STATES = {"已回复", "实际回复", "疑似回复", "看似回复"}
BLOCKING_SEQUENCE_STATES = {"已暂停", "已停止", "已关闭", "已回复"}


def _parse_date_or_datetime(value: object) -> date:
    text = str(value or "").strip()
    if not text:
        raise ValueError("missing date")
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).date()
    except ValueError:
        return datetime.strptime(text, "%Y-%m-%d").date()


def _holiday_set(holidays: Iterable[str | date]) -> set[date]:
    result: set[date] = set()
    for value in holidays:
        if isinstance(value, date):
            result.add(value)
        else:
            result.add(_parse_date_or_datetime(value))
    return result


def _next_workday(value: date, *, holidays: set[date]) -> date:
    current = value
    while current.weekday() >= 5 or current in holidays:
        current += timedelta(days=1)
    return current


def calculate_follow_up_date(
    actual_sent_at: str, *, workdays: int, holidays: Iterable[str | date] = ()
) -> str:
    """Calculate a follow-up date from a real send timestamp.

    Counting starts on the day after the send. Monday-Friday are workdays unless
    the caller supplies a local holiday calendar.
    """

    if workdays <= 0:
        raise ValueError("workdays must be positive")
    current = _parse_date_or_datetime(actual_sent_at)
    holiday_dates = _holiday_set(holidays)
    counted = 0
    while counted < workdays:
        current += timedelta(days=1)
        if current.weekday() < 5 and current not in holiday_dates:
            counted += 1
    return current.isoformat()


def calculate_regular_cadence_date(
    regular_cadence_anchor: str, *, holidays: Iterable[str | date] = ()
) -> str:
    """Add ten calendar days, then move a weekend/holiday to the next workday."""

    anchor = _parse_date_or_datetime(regular_cadence_anchor)
    unadjusted = anchor + timedelta(days=10)
    return _next_workday(unadjusted, holidays=_holiday_set(holidays)).isoformat()


def select_due_records(
    records: Iterable[dict], *, now: datetime
) -> list[dict]:
    """Return unique eligible records due on or before ``now``.

    The caller supplies normalized records from a named local workbook. A record
    is intentionally ignored if a reply, a stop, a risk pause, an unreviewed
    draft, or an invalid date is present. The function treats missed runs as a
    catch-up by accepting overdue dates.
    """

    selected: list[dict] = []
    seen: set[tuple[str, str, str]] = set()

    for record in records:
        due_value = record.get("recommended_next_date") or record.get(
            "next_action_date"
        )
        try:
            due_date = datetime.strptime(str(due_value), "%Y-%m-%d").date()
        except (TypeError, ValueError):
            continue

        if due_date > now.date():
            continue
        if record.get("risk_gate") in BLOCKING_RISK_STATES:
            continue
        if record.get("response_state") in BLOCKING_RESPONSE_STATES:
            continue
        if record.get("sequence_status") in BLOCKING_SEQUENCE_STATES:
            continue
        if record.get("stop_requested") or record.get("has_unreviewed_draft"):
            continue
        if record.get("content_status") == "草稿":
            continue
        if not str(record.get("date_basis_touch_id", "")).strip():
            continue
        try:
            _parse_date_or_datetime(record.get("date_basis_actual_sent_at"))
        except (TypeError, ValueError):
            continue
        if not str(record.get("new_value_or_question", "")).strip():
            continue

        key = (
            str(record.get("customer_id", "")),
            str(record.get("touch_stage", "")),
            due_date.isoformat(),
        )
        if not all(key) or key in seen:
            continue
        seen.add(key)
        selected.append(record)

    return selected


def _blocked_reasons(record: dict, *, now: datetime) -> list[str]:
    due_value = record.get("recommended_next_date") or record.get("next_action_date")
    try:
        due_date = _parse_date_or_datetime(due_value)
    except (TypeError, ValueError):
        return []
    if due_date > now.date():
        return []

    reasons: list[str] = []
    if record.get("risk_gate") in BLOCKING_RISK_STATES:
        reasons.append("风险门暂停或关闭")
    if record.get("response_state") in BLOCKING_RESPONSE_STATES:
        reasons.append("已收到或疑似收到回复")
    if record.get("sequence_status") in BLOCKING_SEQUENCE_STATES:
        reasons.append("触达序列已暂停、停止、回复或关闭")
    if record.get("stop_requested"):
        reasons.append("存在拒绝、停止、退信或关闭状态")
    if record.get("has_unreviewed_draft") or record.get("content_status") == "草稿":
        reasons.append("同一节点已有未审核草稿")
    if not str(record.get("date_basis_touch_id", "")).strip():
        reasons.append("缺少日期基准触达编号")
    try:
        _parse_date_or_datetime(record.get("date_basis_actual_sent_at"))
    except (TypeError, ValueError):
        reasons.append("缺少可追溯实际发送基准")
    if not str(record.get("new_value_or_question", "")).strip():
        reasons.append("缺少新价值或待验证问题")
    if not str(record.get("customer_id", "")).strip() or not str(
        record.get("touch_stage", "")
    ).strip():
        reasons.append("缺少客户编号或触达阶段")
    return reasons


def build_daily_review_packet(
    records: Iterable[dict],
    *,
    now: datetime,
    timezone_name: str = "Asia/Shanghai",
    holidays: Iterable[str | date] = (),
) -> dict:
    """Build one review task for a scheduled local workday run.

    This is a deterministic packet only. It neither opens a Codex task nor writes
    a workbook. A live scheduler and writer remain separate authorized actions.
    """

    timezone = ZoneInfo(timezone_name)
    local_now = now.replace(tzinfo=timezone) if now.tzinfo is None else now.astimezone(timezone)
    holiday_dates = _holiday_set(holidays)
    scheduled = (
        local_now.weekday() < 5
        and local_now.date() not in holiday_dates
        and (local_now.hour, local_now.minute) >= (10, 0)
    )
    record_list = list(records)
    due_records = select_due_records(record_list, now=local_now) if scheduled else []
    due_records.sort(
        key=lambda item: (
            str(item.get("recommended_next_date") or item.get("next_action_date") or ""),
            str(item.get("customer_id") or ""),
            str(item.get("touch_stage") or ""),
        )
    )
    run_date = local_now.date().isoformat()
    blocked_records = []
    if scheduled:
        for record in record_list:
            reasons = _blocked_reasons(record, now=local_now)
            if reasons:
                blocked_records.append(
                    {
                        "customer_id": str(record.get("customer_id") or ""),
                        "touch_stage": str(record.get("touch_stage") or ""),
                        "recommended_next_date": str(
                            record.get("recommended_next_date")
                            or record.get("next_action_date")
                            or ""
                        ),
                        "reasons": reasons,
                    }
                )
    blocked_records.sort(
        key=lambda item: (
            item["recommended_next_date"],
            item["customer_id"],
            item["touch_stage"],
        )
    )
    return {
        "task_type": "daily_due_draft_review",
        "review_task_id": f"due-draft-review-{run_date}",
        "timezone": timezone_name,
        "scheduled_check": scheduled,
        "checked_at": local_now.isoformat(),
        "due_records": due_records,
        "blocked_records": blocked_records,
        "send_allowed": False,
    }
