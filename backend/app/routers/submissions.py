from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.authz import can_review_mission
from app.database import get_db
from app.deps import get_current_user
from app.models import Certification, Submission, User, utcnow
from app.present import present_certification, present_submission
from app.queries import membership_for
from app.schemas import ReviewIn, ReviewResult, SubmissionOut

router = APIRouter(prefix="/submissions", tags=["submissions"])


def _tags(values: list[str]) -> list[str]:
    cleaned: list[str] = []
    seen: set[str] = set()
    for raw in values:
        tag = " ".join(raw.split())
        key = tag.lower()
        if not tag or key in seen:
            continue
        if len(tag) < 2 or len(tag) > 60:
            raise HTTPException(status_code=400, detail="Each competency tag must be 2 to 60 characters.")
        seen.add(key)
        cleaned.append(tag)
    if len(cleaned) > 8:
        raise HTTPException(status_code=400, detail="Use at most 8 competency tags.")
    return cleaned


def _join(items: list[str]) -> str:
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + f", and {items[-1]}"


def _load(db: Session, submission_id: int) -> Submission:
    submission = db.get(Submission, submission_id)
    if submission is None:
        raise HTTPException(status_code=404, detail="Submission not found.")
    return submission


def _can_view(user: User, submission: Submission) -> bool:
    if user.id == submission.user_id:
        return True
    return can_review_mission(user, submission.mission)


@router.get("/{submission_id}", response_model=SubmissionOut)
def get_submission(
    submission_id: int,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> dict:
    submission = _load(db, submission_id)
    if not _can_view(user, submission):
        raise HTTPException(status_code=404, detail="Submission not found.")
    return present_submission(db, submission, user)


@router.post("/{submission_id}/review", response_model=ReviewResult)
def review_submission(
    submission_id: int,
    body: ReviewIn,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> dict:
    submission = _load(db, submission_id)
    mission = submission.mission
    if not can_review_mission(user, mission):
        if user.id == submission.user_id:
            raise HTTPException(status_code=403, detail="Only the mission's employer can certify this submission.")
        raise HTTPException(status_code=404, detail="Submission not found.")
    if submission.status == "approved":
        raise HTTPException(status_code=409, detail="This submission is already certified.")
    membership = membership_for(db, submission.user_id, mission.id)
    if membership is None:
        raise HTTPException(status_code=409, detail="This submission has no mission membership.")
    now = utcnow()
    if body.action == "request_changes":
        if len(body.feedback) < 10:
            raise HTTPException(status_code=400, detail="Tell the learner what to change (at least 10 characters).")
        submission.status = "changes_requested"
        submission.feedback = body.feedback
        submission.updated_at = now
        membership.status = "changes_requested"
        db.commit()
        return {"submission": present_submission(db, submission, user), "certification": None}

    tags = _tags(body.competency_tags)
    if not tags:
        raise HTTPException(status_code=400, detail="Add at least one competency tag to issue a certification.")
    learner = submission.user
    statement = (
        f"{mission.organization.name} certifies that {learner.full_name} demonstrated "
        f"{_join(tags)} on the mission \"{mission.title}\"."
    )
    certification = Certification(
        user_id=learner.id,
        submission_id=submission.id,
        mission_id=mission.id,
        issuer_user_id=user.id,
        issuer_name=user.full_name,
        organization_name=mission.organization.name,
        competency_tags=tags,
        statement=statement,
        issued_at=now,
    )
    submission.status = "approved"
    submission.feedback = body.feedback
    submission.updated_at = now
    membership.status = "certified"
    db.add(certification)
    db.commit()
    db.refresh(certification)
    return {
        "submission": present_submission(db, submission, user),
        "certification": present_certification(certification),
    }
