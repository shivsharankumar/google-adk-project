import re
import sqlite3
from datetime import datetime,timedelta,timezone
from pathlib import Path
from google.adk.tools import ToolContext

DB_PATH = Path(__file__).resolve().parent / "edtech.db"

REFUND_WINDOWS_DAYS=7
MAX_COMPLETION_PERCENT=20

REFUND_POLICY = (
    f"Refund policy: a refund can be requested within {REFUND_WINDOWS_DAYS} days of purchase, "
    f"provided you have completed no more than {MAX_COMPLETION_PERCENT}% of the course. "
    "Refunds are for the full amount paid. Only active enrollments are eligible; enrollments "
    "already refunded or with a pending refund request cannot be requested again."
)


def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _now():
    return datetime.now(timezone.utc)


def identify_student(email: str) -> dict:
    """Finds the student using their registered email."""
    with _conn() as conn:
        row = conn.execute(
            "SELECT student_id, name, email FROM student WHERE lower(email) = lower(?)",
            (email.strip(),),
        ).fetchone()
    if not row:
        return {"found": False, "message": f"No student registered with email '{email}'."}
    return {"found": True, **dict(row)}


def get_my_enrollments(student_id: str) -> dict:
    """Retrieves a student's enrollments (with course details) to identify the course."""
    with _conn() as conn:
        rows = conn.execute(
            """SELECT e.enrollment_id, e.course_id, c.course_name, e.purchased_at,
                      e.amount_paid, e.completion_percentage, e.status, e.refund_reason
               FROM enrollments e JOIN course c ON c.course_id = e.course_id
               WHERE e.student_id = ? ORDER BY e.purchased_at DESC""",
            (student_id,),
        ).fetchall()
    return {"student_id": student_id, "count": len(rows), "enrollments": [dict(r) for r in rows]}


def get_refund_policy() -> dict:
    """Returns the common refund policy."""
    return {
        "policy": REFUND_POLICY,
        "window_days": REFUND_WINDOWS_DAYS,
        "max_completion_pct": MAX_COMPLETION_PERCENT,
    }


def check_refund_eligibility(enrollment_id: str) -> dict:
    """Checks enrollment status, purchase age, and course completion."""
    with _conn() as conn:
        row = conn.execute(
            "SELECT * FROM enrollments WHERE enrollment_id = ?", (enrollment_id,)
        ).fetchone()
    if not row:
        return {"eligible": False, "reasons": [f"Enrollment '{enrollment_id}' not found."]}

    age_days = (_now() - datetime.fromisoformat(row["purchased_at"])).days
    reasons = []
    if row["status"] != "active":
        reasons.append(f"Enrollment status is '{row['status']}', not 'active'.")
    if age_days > REFUND_WINDOWS_DAYS:
        reasons.append(f"Purchased {age_days} days ago; window is {REFUND_WINDOWS_DAYS} days.")
    if row["completion_percentage"] > MAX_COMPLETION_PERCENT:
        reasons.append(
            f"Course is {row['completion_percentage']}% complete; max allowed is {MAX_COMPLETION_PERCENT}%."
        )
    return {
        "enrollment_id": enrollment_id,
        "eligible": not reasons,
        "refund_amount": row["amount_paid"],
        "status": row["status"],
        "purchase_age_days": age_days,
        "completion_percentage": row["completion_percentage"],
        "reasons": reasons or ["Meets all refund criteria."],
    }


def request_refund(enrollment_id: str, reason: str, confirmed: bool = False) -> dict:
    """Gets confirmation, then saves the refund request with its reason."""
    check = check_refund_eligibility(enrollment_id)
    if not check["eligible"]:
        return {"submitted": False, "message": "Not eligible for refund.", "reasons": check["reasons"]}
    if not confirmed:
        return {
            "submitted": False,
            "needs_confirmation": True,
            "refund_amount": check["refund_amount"],
            "message": f"Please confirm a full refund of Rs {check['refund_amount']} for {enrollment_id} "
                       f"with reason: '{reason}'. Call again with confirmed=True.",
        }
    with _conn() as conn:
        conn.execute(
            "UPDATE enrollments SET status = 'refund_requested', refund_reason = ? WHERE enrollment_id = ?",
            (reason, enrollment_id),
        )
    return {"submitted": True, "enrollment_id": enrollment_id, "status": "refund_requested",
            "reason": reason, "refund_amount": check["refund_amount"]}


def get_refund_status(enrollment_id: str) -> dict:
    """Checks the status of the refund request afterward."""
    with _conn() as conn:
        row = conn.execute(
            "SELECT enrollment_id, status, refund_reason FROM enrollments WHERE enrollment_id = ?",
            (enrollment_id,),
        ).fetchone()
    if not row:
        return {"found": False, "message": f"Enrollment '{enrollment_id}' not found."}
    if row["status"] == "active":
        return {"found": True, **dict(row), "message": "No refund has been requested."}
    return {"found": True, **dict(row)}