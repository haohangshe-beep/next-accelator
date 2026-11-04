from __future__ import annotations

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, get_optional_user
from app.models import Mission, MissionMembership, SkillModule, Submission, User, utcnow
from app.present import present_mission_detail, present_mission_summary, present_submission
from app.queries import completed_codes, membership_for, submission_for
from app.schemas import MissionCreate, MissionDetail, MissionSummary, SubmissionOut, SubmitIn
from app.tracks import TRACK_LABELS

router = APIRouter(prefix="/missions", tags=["missions"])


def _get_mission(db: Session, mission_id: int) -> Mission:
    mission = db.get(Mission, mission_id)
    if mission is None:
        raise HTTPException(status_code=404, detail="Mission not found.")
    return mission


def _known_codes(db: Session, codes: list[str]) -> None:
    if not codes:
        return
    found = set(db.scalars(select(SkillModule.code).where(SkillModule.code.in_(codes))).all())
    missing = [code for code in codes if code not in found]
    if missing:
        raise HTTPException(status_code=400, detail="Unknown skill codes: " + ", ".join(missing))


@router.get("", response_model=list[MissionSummary])
def list_missions(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User | None, Depends(get_optional_user)],
    track: str | None = None,
    skill: str | None = None,
) -> list[dict]:
    if track:
        if track not in TRACK_LABELS:
            raise HTTPException(
                status_code=400,
                detail="Unknown track. Use AI, NewSpace, Robotics, or LowAltitude.",
            )
    skill_code = skill.strip().upper() if skill else None
    missions = db.scalars(select(Mission).order_by(Mission.id)).all()
    if track:
        missions = [mission for mission in missions if mission.track == track]
    if skill_code:
        missions = [mission for mission in missions if skill_code in (mission.required_skill_codes or [])]
    memberships: dict[int, MissionMembership] = {}
    if user is not None:
        rows = db.scalars(select(MissionMembership).where(MissionMembership.user_id == user.id)).all()
        memberships = {row.mission_id: row for row in rows}
    return [present_mission_summary(mission, memberships.get(mission.id)) for mission in missions]


@router.post("", response_model=MissionDetail, status_code=201)
def create_mission(
    body: MissionCreate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> dict:
    if user.role != "employer" or user.organization_id is None:
        raise HTTPException(status_code=403, detail="Only an employer with an organisation can publish a mission.")
    _known_codes(db, body.required_skill_codes)
    deadline = date.fromisoformat(body.deadline) if body.deadline else None
    mission = Mission(
        title=body.title,
        organization_id=user.organization_id,
        track=body.track.value,
        difficulty=body.difficulty,
        summary=body.summary,
        problem_statement=body.problem_statement,
        deliverables=body.deliverables,
        required_skill_codes=body.required_skill_codes,
        suggested_competencies=body.suggested_competencies,
        deadline=deadline,
        status="open",
        created_by=user.id,
        created_at=utcnow(),
    )
    db.add(mission)
    db.commit()
    db.refresh(mission)
    return present_mission_detail(db, mission, user)


@router.get("/{mission_id}", response_model=MissionDetail)
def get_mission(
    mission_id: int,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User | None, Depends(get_optional_user)],
) -> dict:
    mission = _get_mission(db, mission_id)
    return present_mission_detail(db, mission, user)


@router.post("/{mission_id}/join", response_model=MissionDetail)
def join_mission(
    mission_id: int,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> dict:
    if user.role != "learner":
        raise HTTPException(status_code=403, detail="Only learners can join a mission.")
    mission = _get_mission(db, mission_id)
    existing = membership_for(db, user.id, mission.id)
    if existing is not None:
        return present_mission_detail(db, mission, user)
    if mission.status != "open":
        raise HTTPException(status_code=400, detail="This mission is closed.")
    done = completed_codes(db, user.id)
    missing = [code for code in (mission.required_skill_codes or []) if code not in done]
    if missing:
        raise HTTPException(
            status_code=400,
            detail="Complete the required modules before joining: " + ", ".join(missing),
        )
    db.add(MissionMembership(mission_id=mission.id, user_id=user.id, status="joined", joined_at=utcnow()))
    db.commit()
    return present_mission_detail(db, mission, user)


@router.post("/{mission_id}/submit", response_model=SubmissionOut)
def submit_mission(
    mission_id: int,
    body: SubmitIn,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> dict:
    if user.role != "learner":
        raise HTTPException(status_code=403, detail="Only learners submit mission evidence.")
    mission = _get_mission(db, mission_id)
    membership = membership_for(db, user.id, mission.id)
    if membership is None:
        raise HTTPException(status_code=400, detail="Join the mission before submitting evidence.")
    existing = submission_for(db, user.id, mission.id)
    now = utcnow()
    if existing is not None:
        if existing.status == "pending":
            raise HTTPException(status_code=409, detail="This deliverable is already waiting for review.")
        if existing.status == "approved":
            raise HTTPException(status_code=409, detail="This mission is already certified.")
        existing.deliverable_url = body.deliverable_url
        existing.notes = body.notes
        existing.status = "pending"
        existing.feedback = ""
        existing.updated_at = now
        membership.status = "submitted"
        db.commit()
        return present_submission(db, existing, user)
    submission = Submission(
        mission_id=mission.id,
        user_id=user.id,
        deliverable_url=body.deliverable_url,
        notes=body.notes,
        status="pending",
        feedback="",
        created_at=now,
        updated_at=now,
    )
    membership.status = "submitted"
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return present_submission(db, submission, user)
