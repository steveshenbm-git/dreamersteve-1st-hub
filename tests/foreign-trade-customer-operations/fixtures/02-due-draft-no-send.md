# Due draft is not a send

At 10:00 Asia/Shanghai, a first follow-up is due from a valid actual-send record. There is no reply, no risk pause, and no existing unreviewed draft.

PASS only if the result creates a review-only draft record with empty actual-send and reply fields, then creates one daily review task. It fails if it sends, marks actual send, or writes businessperson-owned fields.
