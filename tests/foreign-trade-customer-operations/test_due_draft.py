from datetime import datetime
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from foreign_trade_due_draft import (
    build_daily_review_packet,
    calculate_follow_up_date,
    calculate_regular_cadence_date,
    select_due_records,
)


class DueDraftSelectionTests(unittest.TestCase):
    def test_due_record_is_selected_once(self):
        records = [
            {
                "customer_id": "C-001",
                "touch_stage": "第一次邮件跟进",
                "recommended_next_date": "2026-07-28",
                "date_basis_touch_id": "T-000",
                "date_basis_actual_sent_at": "2026-07-21T09:00:00+08:00",
                "new_value_or_question": "验证当前应用要求",
                "content_status": "计划触达",
                "sequence_status": "进行中",
                "risk_gate": "未触发",
                "response_state": "无回复",
                "stop_requested": False,
                "has_unreviewed_draft": False,
            },
            {
                "customer_id": "C-001",
                "touch_stage": "第一次邮件跟进",
                "recommended_next_date": "2026-07-28",
                "date_basis_touch_id": "T-000",
                "date_basis_actual_sent_at": "2026-07-21T09:00:00+08:00",
                "new_value_or_question": "验证当前应用要求",
                "content_status": "计划触达",
                "sequence_status": "进行中",
                "risk_gate": "未触发",
                "response_state": "无回复",
                "stop_requested": False,
                "has_unreviewed_draft": False,
            },
        ]

        selected = select_due_records(
            records, now=datetime(2026, 7, 28, 10, 0)
        )

        self.assertEqual(1, len(selected))
        self.assertEqual("C-001", selected[0]["customer_id"])

    def test_reply_risk_pause_and_unreviewed_draft_block_selection(self):
        records = [
            {
                "customer_id": "C-reply",
                "touch_stage": "第二次邮件跟进",
                "recommended_next_date": "2026-07-28",
                "date_basis_touch_id": "T-r1",
                "date_basis_actual_sent_at": "2026-07-17T09:00:00+08:00",
                "new_value_or_question": "新问题",
                "content_status": "计划触达",
                "sequence_status": "进行中",
                "risk_gate": "未触发",
                "response_state": "已回复",
                "stop_requested": False,
                "has_unreviewed_draft": False,
            },
            {
                "customer_id": "C-risk",
                "touch_stage": "第二次邮件跟进",
                "recommended_next_date": "2026-07-28",
                "date_basis_touch_id": "T-risk",
                "date_basis_actual_sent_at": "2026-07-17T09:00:00+08:00",
                "new_value_or_question": "新问题",
                "content_status": "计划触达",
                "sequence_status": "进行中",
                "risk_gate": "暂停待业务员审核",
                "response_state": "无回复",
                "stop_requested": False,
                "has_unreviewed_draft": False,
            },
            {
                "customer_id": "C-draft",
                "touch_stage": "第二次邮件跟进",
                "recommended_next_date": "2026-07-28",
                "date_basis_touch_id": "T-draft",
                "date_basis_actual_sent_at": "2026-07-17T09:00:00+08:00",
                "new_value_or_question": "新问题",
                "content_status": "草稿",
                "sequence_status": "进行中",
                "risk_gate": "未触发",
                "response_state": "无回复",
                "stop_requested": False,
                "has_unreviewed_draft": True,
            },
        ]

        self.assertEqual(
            [], select_due_records(records, now=datetime(2026, 7, 28, 10, 0))
        )

    def test_missing_actual_send_basis_or_new_value_blocks_selection(self):
        base = {
            "customer_id": "C-001",
            "touch_stage": "第一次邮件跟进",
            "recommended_next_date": "2026-07-28",
            "date_basis_touch_id": "T-000",
            "date_basis_actual_sent_at": "2026-07-21T09:00:00+08:00",
            "new_value_or_question": "验证当前应用要求",
            "content_status": "计划触达",
            "sequence_status": "进行中",
            "risk_gate": "未触发",
            "response_state": "无回复",
            "stop_requested": False,
            "has_unreviewed_draft": False,
        }
        no_send = dict(base, date_basis_actual_sent_at="")
        no_value = dict(base, customer_id="C-002", new_value_or_question="")

        self.assertEqual(
            [], select_due_records([no_send, no_value], now=datetime(2026, 7, 28, 10, 0))
        )

    def test_follow_up_and_regular_dates_use_the_approved_rules(self):
        self.assertEqual(
            "2026-07-28",
            calculate_follow_up_date("2026-07-21T09:00:00+08:00", workdays=5),
        )
        self.assertEqual(
            "2026-08-03",
            calculate_regular_cadence_date("2026-07-22T09:00:00+08:00"),
        )

    def test_one_daily_review_packet_contains_all_due_records(self):
        records = []
        for customer_id in ("C-001", "C-002"):
            records.append(
                {
                    "customer_id": customer_id,
                    "touch_stage": "第一次邮件跟进",
                    "recommended_next_date": "2026-07-28",
                    "date_basis_touch_id": f"T-{customer_id}",
                    "date_basis_actual_sent_at": "2026-07-21T09:00:00+08:00",
                    "new_value_or_question": "验证当前应用要求",
                    "content_status": "计划触达",
                    "sequence_status": "进行中",
                    "risk_gate": "未触发",
                    "response_state": "无回复",
                    "stop_requested": False,
                    "has_unreviewed_draft": False,
                }
            )

        packet = build_daily_review_packet(
            records, now=datetime(2026, 7, 28, 10, 0)
        )

        self.assertEqual("daily_due_draft_review", packet["task_type"])
        self.assertEqual(2, len(packet["due_records"]))
        self.assertEqual(False, packet["send_allowed"])

    def test_due_but_not_draftable_record_is_reported_with_a_reason(self):
        record = {
            "customer_id": "C-gap",
            "touch_stage": "定期触达",
            "recommended_next_date": "2026-07-28",
            "date_basis_touch_id": "T-gap",
            "date_basis_actual_sent_at": "2026-07-18T09:00:00+08:00",
            "new_value_or_question": "",
            "content_status": "计划触达",
            "sequence_status": "进行中",
            "risk_gate": "未触发",
            "response_state": "无回复",
            "stop_requested": False,
            "has_unreviewed_draft": False,
        }

        packet = build_daily_review_packet(
            [record], now=datetime(2026, 7, 28, 10, 0)
        )

        self.assertEqual([], packet["due_records"])
        self.assertEqual("缺少新价值或待验证问题", packet["blocked_records"][0]["reasons"][0])

    def test_weekend_or_before_ten_is_not_a_scheduled_run(self):
        packet = build_daily_review_packet(
            [], now=datetime(2026, 8, 1, 10, 0)
        )
        self.assertEqual(False, packet["scheduled_check"])
        self.assertEqual([], packet["due_records"])

        packet = build_daily_review_packet(
            [], now=datetime(2026, 7, 31, 9, 59)
        )
        self.assertEqual(False, packet["scheduled_check"])

    def test_configured_holiday_is_skipped_and_daily_task_id_is_stable(self):
        holiday_packet = build_daily_review_packet(
            [],
            now=datetime(2026, 10, 1, 10, 0),
            holidays=["2026-10-01"],
        )
        self.assertEqual(False, holiday_packet["scheduled_check"])

        morning_packet = build_daily_review_packet(
            [], now=datetime(2026, 7, 31, 10, 0)
        )
        later_packet = build_daily_review_packet(
            [], now=datetime(2026, 7, 31, 15, 30)
        )
        self.assertEqual(
            morning_packet["review_task_id"], later_packet["review_task_id"]
        )


if __name__ == "__main__":
    unittest.main()
