from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import MissionMembership, ModuleCompletion, SkillModule, Submission


def completed_codes(db: Session, user_id: int) -> set[str]:
    rows = db.scalars(
        select(SkillModule.code)
        .join(ModuleCompletion, ModuleCompletion.module_id == SkillModule.id)
        .where(ModuleCompletion.user_id == user_id)
    ).all()
    return set(rows)


def completion_for(db: Session, user_id: int, module_id: int) -> ModuleCompletion | None:
    return db.scalar(
        select(ModuleCompletion).where(
            ModuleCompletion.user_id == user_id,
            ModuleCompletion.module_id == module_id,
        )
    )


def completions_by_module(db: Session, user_id: int) -> dict[int, ModuleCompletion]:
    rows = db.scalars(select(ModuleCompletion).where(ModuleCompletion.user_id == user_id)).all()
    return {row.module_id: row for row in rows}


def membership_for(db: Session, user_id: int, mission_id: int) -> MissionMembership | None:
    return db.scalar(
        select(MissionMembership).where(
            MissionMembership.user_id == user_id,
            MissionMembership.mission_id == mission_id,
        )
    )


def submission_for(db: Session, user_id: int, mission_id: int) -> Submission | None:
    return db.scalar(
        select(Submission).where(Submission.user_id == user_id, Submission.mission_id == mission_id)
    )
