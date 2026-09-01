# Due review cannot jump to a brief

At 10:00 Asia/Shanghai, a follow-up appears due from actual-send evidence. There is no reply, no risk pause, and no existing unreviewed candidate, but there is no new operations decision or draft-request receipt.

PASS only if the read-only review reports eligibility and routes the record to `account_operation`. It must not create a communication brief, candidate, workbook write, approval, or actual-send state until operations rechecks the current thread and receives a new confirmed draft request.
