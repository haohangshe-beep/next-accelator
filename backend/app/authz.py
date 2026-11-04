from __future__ import annotations

from app.models import Mission, User


def can_review_mission(user: User, mission: Mission) -> bool:
    if user.role == "admin":
        return True
    return (
        user.role == "employer"
        and user.organization_id is not None
        and user.organization_id == mission.organization_id
    )
