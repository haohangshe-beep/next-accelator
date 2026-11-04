"""Canonical track codes and the English labels shown in the product."""

from __future__ import annotations

TRACK_LABELS: dict[str, str] = {
    "AI": "AI",
    "NewSpace": "NewSpace",
    "Robotics": "Robotics",
    "LowAltitude": "Low Altitude Economy",
}

LEVELS = ("Foundation", "Intermediate", "Advanced")
DIFFICULTIES = ("Introductory", "Intermediate", "Advanced")
ROLES = ("learner", "employer", "admin")
MISSION_STATUSES = ("open", "closed")
MEMBERSHIP_STATUSES = ("joined", "submitted", "changes_requested", "certified")
SUBMISSION_STATUSES = ("pending", "changes_requested", "approved")
WAITLIST_TOPICS = ("talent", "apprenticeships")


def in_check(column: str, values: tuple[str, ...]) -> str:
    quoted = ", ".join(f"'{value}'" for value in values)
    return f"{column} IN ({quoted})"
