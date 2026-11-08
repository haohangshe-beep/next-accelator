"""Rule-based career navigator. No model calls — recommendations follow completed modules and interests."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Mission, MissionMembership, SkillModule, Submission, User
from app.queries import completed_codes
from app.tracks import TRACK_LABELS


def _rec(
    rec_id: str,
    kind: str,
    title: str,
    reason: str,
    action_label: str,
    href: str,
) -> dict[str, str]:
    return {
        "id": rec_id,
        "kind": kind,
        "title": title,
        "reason": reason,
        "action_label": action_label,
        "href": href,
    }


def recommend(db: Session, user: User) -> list[dict[str, str]]:
    modules = db.scalars(select(SkillModule).order_by(SkillModule.code)).all()
    by_code = {module.code: module for module in modules}
    done = completed_codes(db, user.id)
    interests = [track for track in (user.interests or []) if track in TRACK_LABELS]
    interest_set = set(interests)

    tracks_with_progress = {by_code[code].track for code in done if code in by_code}
    memberships = db.scalars(select(MissionMembership).where(MissionMembership.user_id == user.id)).all()
    membership_by_mission = {row.mission_id: row for row in memberships}
    submissions = db.scalars(select(Submission).where(Submission.user_id == user.id)).all()
    submission_by_mission = {row.mission_id: row for row in submissions}
    missions = db.scalars(select(Mission).where(Mission.status == "open").order_by(Mission.id)).all()

    recs: list[dict[str, str]] = []

    for submission in submissions:
        if submission.status != "changes_requested":
            continue
        mission = submission.mission
        recs.append(
            _rec(
                f"resubmit-{submission.id}",
                "submission",
                f"Update your evidence for {mission.title}",
                "The employer asked for changes. Revise the deliverable and submit it again.",
                "Review feedback",
                f"/missions/{mission.id}",
            )
        )

    for membership in memberships:
        if membership.status != "joined":
            continue
        mission = membership.mission
        recs.append(
            _rec(
                f"submit-{mission.id}",
                "submission",
                f"Submit evidence for {mission.title}",
                "You have joined this mission. Add a deliverable URL and a short note so an employer can review it.",
                "Submit evidence",
                f"/missions/{mission.id}",
            )
        )

    for module in modules:
        if module.code in done:
            continue
        prerequisites = list(module.prerequisites or [])
        if not all(code in done for code in prerequisites):
            continue
        if module.track not in tracks_with_progress:
            continue
        label = TRACK_LABELS.get(module.track, module.track)
        recs.append(
            _rec(
                f"continue-{module.code}",
                "module",
                f"Complete {module.title}",
                f"You already have a completion on the {label} track. {module.code} is the next module whose prerequisites you have met.",
                "Open module",
                f"/skills/{module.code}",
            )
        )

    qualified: list[Mission] = []
    for mission in missions:
        if mission.id in membership_by_mission:
            continue
        required = list(mission.required_skill_codes or [])
        if all(code in done for code in required):
            qualified.append(mission)
    qualified.sort(key=lambda mission: (0 if mission.track in interest_set else 1, mission.id))
    for mission in qualified[:2]:
        required = list(mission.required_skill_codes or [])
        label = TRACK_LABELS.get(mission.track, mission.track)
        if required:
            reason = (
                f"You meet the required modules ({', '.join(required)}). "
                f"Join this {label} mission and submit a deliverable."
            )
        else:
            reason = f"This {label} mission has no prerequisite modules. You can join it now."
        recs.append(
            _rec(
                f"join-{mission.id}",
                "mission",
                f"Join {mission.title}",
                reason,
                "View mission",
                f"/missions/{mission.id}",
            )
        )

    started_interest_tracks: set[str] = set()
    for module in modules:
        if module.code in done or module.track in tracks_with_progress:
            continue
        if module.track not in interest_set or module.track in started_interest_tracks:
            continue
        prerequisites = list(module.prerequisites or [])
        if prerequisites and not all(code in done for code in prerequisites):
            continue
        if prerequisites:
            continue
        started_interest_tracks.add(module.track)
        label = TRACK_LABELS.get(module.track, module.track)
        recs.append(
            _rec(
                f"start-{module.code}",
                "module",
                f"Start {module.title}",
                f"{label} is one of your interests, and you have not recorded a module on that track yet. {module.code} is the foundation.",
                "Open module",
                f"/skills/{module.code}",
            )
        )

    if done:
        recs.append(
            _rec(
                "share-passport",
                "passport",
                "Share your Skills Passport",
                "You have recorded skills. Copy your public passport link when you apply or follow up with an employer.",
                "Open passport",
                f"/passport/{user.slug}",
            )
        )

    if len(recs) < 3:
        for module in modules:
            if module.code in done:
                continue
            prerequisites = list(module.prerequisites or [])
            if not all(code in done for code in prerequisites):
                continue
            label = TRACK_LABELS.get(module.track, module.track)
            recs.append(
                _rec(
                    f"open-{module.code}",
                    "module",
                    f"Start {module.title}",
                    f"{module.code} is an open {label} module. Finishing it writes a record onto your Skills Passport.",
                    "Open module",
                    f"/skills/{module.code}",
                )
            )
            if len(recs) >= 3:
                break

    if len(recs) < 3:
        for mission in missions:
            if mission.id in membership_by_mission or mission.id in submission_by_mission:
                continue
            required = [code for code in (mission.required_skill_codes or []) if code not in done]
            if not required:
                continue
            label = TRACK_LABELS.get(mission.track, mission.track)
            recs.append(
                _rec(
                    f"stretch-{mission.id}",
                    "mission",
                    f"Build toward {mission.title}",
                    f"This {label} mission needs {', '.join(required)}. Complete those modules, then join.",
                    "View mission",
                    f"/missions/{mission.id}",
                )
            )
            if len(recs) >= 3:
                break

    if len(recs) < 3:
        recs.append(
            _rec(
                "browse-skills",
                "module",
                "Browse the skills catalogue",
                "Pick a foundation module in AI, NewSpace, Robotics, or Low Altitude Economy.",
                "Browse skills",
                "/skills",
            )
        )

    unique: list[dict[str, str]] = []
    seen: set[str] = set()
    for rec in recs:
        if rec["id"] in seen:
            continue
        seen.add(rec["id"])
        unique.append(rec)
    return unique[:6]
