from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.authz import can_review_mission
from app.models import (
    Certification,
    Mission,
    MissionMembership,
    ModuleCompletion,
    SkillModule,
    Submission,
    User,
    WaitlistEntry,
)
from app.queries import completed_codes, membership_for, submission_for


def iso(value: datetime | date | str | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.isoformat()
    return value.isoformat()


def present_user(user: User) -> dict:
    organization = user.organization
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "slug": user.slug,
        "headline": user.headline,
        "bio": user.bio,
        "interests": list(user.interests or []),
        "organization": None
        if organization is None
        else {"id": organization.id, "name": organization.name, "summary": organization.summary},
    }


def present_module_summary(module: SkillModule, completion: ModuleCompletion | None) -> dict:
    return {
        "code": module.code,
        "title": module.title,
        "track": module.track,
        "level": module.level,
        "summary": module.summary,
        "estimated_hours": module.estimated_hours,
        "prerequisites": list(module.prerequisites or []),
        "completed": completion is not None,
        "completed_at": iso(completion.completed_at) if completion else None,
    }


def present_module_detail(
    module: SkillModule,
    completion: ModuleCompletion | None,
    missing_prerequisites: list[str] | None = None,
) -> dict:
    data = present_module_summary(module, completion)
    data["learning_outcomes"] = list(module.learning_outcomes or [])
    data["checklist"] = list(module.checklist or [])
    data["missing_prerequisites"] = list(missing_prerequisites or [])
    return data


def present_certification(cert: Certification) -> dict:
    return {
        "id": cert.id,
        "mission_id": cert.mission_id,
        "mission_title": cert.mission.title,
        "organization_name": cert.organization_name,
        "issuer_name": cert.issuer_name,
        "competency_tags": list(cert.competency_tags or []),
        "statement": cert.statement,
        "issued_at": iso(cert.issued_at),
    }


def present_submission(db: Session, submission: Submission, viewer: User) -> dict:
    mission = submission.mission
    learner = submission.user
    cert = db.scalar(select(Certification).where(Certification.submission_id == submission.id))
    return {
        "id": submission.id,
        "mission_id": submission.mission_id,
        "mission_title": mission.title,
        "mission_track": mission.track,
        "organization_name": mission.organization.name,
        "status": submission.status,
        "deliverable_url": submission.deliverable_url,
        "notes": submission.notes,
        "feedback": submission.feedback,
        "learner_name": learner.full_name,
        "learner_slug": learner.slug,
        "created_at": iso(submission.created_at),
        "updated_at": iso(submission.updated_at),
        "can_review": can_review_mission(viewer, mission),
        "suggested_competencies": list(mission.suggested_competencies or []),
        "certification": present_certification(cert) if cert else None,
    }


def present_mission_summary(mission: Mission, membership: MissionMembership | None) -> dict:
    return {
        "id": mission.id,
        "title": mission.title,
        "organization_name": mission.organization.name,
        "track": mission.track,
        "difficulty": mission.difficulty,
        "summary": mission.summary,
        "required_skill_codes": list(mission.required_skill_codes or []),
        "deadline": iso(mission.deadline),
        "status": mission.status,
        "membership_status": membership.status if membership else None,
    }


def present_mission_detail(db: Session, mission: Mission, viewer: User | None) -> dict:
    membership = membership_for(db, viewer.id, mission.id) if viewer else None
    data = present_mission_summary(mission, membership)
    missing: list[str] = []
    my_submission = None
    submissions: list[dict] = []
    if viewer and viewer.role == "learner":
        done = completed_codes(db, viewer.id)
        missing = [code for code in (mission.required_skill_codes or []) if code not in done]
        mine = submission_for(db, viewer.id, mission.id)
        if mine is not None:
            my_submission = present_submission(db, mine, viewer)
    if viewer and can_review_mission(viewer, mission):
        rows = db.scalars(
            select(Submission).where(Submission.mission_id == mission.id).order_by(Submission.created_at)
        ).all()
        submissions = [present_submission(db, row, viewer) for row in rows]
    data.update(
        {
            "problem_statement": mission.problem_statement,
            "deliverables": mission.deliverables,
            "suggested_competencies": list(mission.suggested_competencies or []),
            "missing_skill_codes": missing,
            "my_submission": my_submission,
            "submissions": submissions,
        }
    )
    return data


def present_passport(db: Session, user: User) -> dict:
    completions = db.scalars(
        select(ModuleCompletion)
        .where(ModuleCompletion.user_id == user.id)
        .order_by(ModuleCompletion.completed_at, ModuleCompletion.id)
    ).all()
    modules = []
    for completion in completions:
        module = completion.module
        modules.append(
            {
                "code": module.code,
                "title": module.title,
                "track": module.track,
                "level": module.level,
                "estimated_hours": module.estimated_hours,
                "completed_at": iso(completion.completed_at),
            }
        )

    memberships = db.scalars(
        select(MissionMembership)
        .where(MissionMembership.user_id == user.id)
        .order_by(MissionMembership.joined_at, MissionMembership.id)
    ).all()
    missions = []
    for membership in memberships:
        mission = membership.mission
        submission = submission_for(db, user.id, mission.id)
        missions.append(
            {
                "id": mission.id,
                "title": mission.title,
                "track": mission.track,
                "organization_name": mission.organization.name,
                "status": membership.status,
                "deliverable_url": submission.deliverable_url if submission else None,
                "joined_at": iso(membership.joined_at),
            }
        )

    certifications = db.scalars(
        select(Certification).where(Certification.user_id == user.id).order_by(Certification.issued_at, Certification.id)
    ).all()
    return {
        "profile": {
            "full_name": user.full_name,
            "slug": user.slug,
            "headline": user.headline,
            "bio": user.bio,
            "interests": list(user.interests or []),
        },
        "modules": modules,
        "missions": missions,
        "certifications": [present_certification(cert) for cert in certifications],
    }


def _count(db: Session, model: type) -> int:
    value = db.scalar(select(func.count()).select_from(model))
    return int(value or 0)


def present_dashboard(db: Session, user: User) -> dict:
    learner = None
    employer = None
    admin = None
    if user.role == "learner":
        submissions = db.scalars(
            select(Submission).where(Submission.user_id == user.id).order_by(Submission.updated_at.desc())
        ).all()
        learner = {
            "completed_modules": _count_where(db, ModuleCompletion, ModuleCompletion.user_id == user.id),
            "missions_joined": _count_where(db, MissionMembership, MissionMembership.user_id == user.id),
            "certifications": _count_where(db, Certification, Certification.user_id == user.id),
            "passport_slug": user.slug,
            "submissions": [
                {
                    "id": row.id,
                    "mission_id": row.mission_id,
                    "mission_title": row.mission.title,
                    "status": row.status,
                    "updated_at": iso(row.updated_at),
                }
                for row in submissions
            ],
        }
    elif user.role == "employer":
        missions = db.scalars(
            select(Mission).where(Mission.organization_id == user.organization_id).order_by(Mission.id)
        ).all()
        pending = db.scalars(
            select(Submission)
            .join(Mission, Mission.id == Submission.mission_id)
            .where(Mission.organization_id == user.organization_id, Submission.status == "pending")
            .order_by(Submission.created_at)
        ).all()
        employer = {
            "organization_name": user.organization.name if user.organization else "",
            "missions": [
                {
                    "id": mission.id,
                    "title": mission.title,
                    "track": mission.track,
                    "status": mission.status,
                    "submission_count": _count_where(db, Submission, Submission.mission_id == mission.id),
                    "pending_count": _count_where(
                        db,
                        Submission,
                        (Submission.mission_id == mission.id) & (Submission.status == "pending"),
                    ),
                }
                for mission in missions
            ],
            "pending_reviews": [
                {
                    "id": row.id,
                    "mission_id": row.mission_id,
                    "mission_title": row.mission.title,
                    "learner_name": row.user.full_name,
                    "learner_slug": row.user.slug,
                    "submitted_at": iso(row.created_at),
                }
                for row in pending
            ],
        }
    elif user.role == "admin":
        admin = {
            "module_count": _count(db, SkillModule),
            "mission_count": _count(db, Mission),
            "user_count": _count(db, User),
            "waitlist_count": _count(db, WaitlistEntry),
        }
    return {"user": present_user(user), "learner": learner, "employer": employer, "admin": admin}


def _count_where(db: Session, model: type, criterion) -> int:
    value = db.scalar(select(func.count()).select_from(model).where(criterion))
    return int(value or 0)
