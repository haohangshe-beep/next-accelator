from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, get_optional_user
from app.models import ModuleCompletion, SkillModule, User, utcnow
from app.present import present_module_detail, present_module_summary
from app.queries import completed_codes, completion_for, completions_by_module
from app.schemas import CompleteModuleIn, CompletionResult, ModuleDetail, ModuleSummary

router = APIRouter(prefix="/modules", tags=["modules"])


def _get_module(db: Session, code: str) -> SkillModule:
    module = db.scalar(select(SkillModule).where(SkillModule.code == code.strip().upper()))
    if module is None:
        raise HTTPException(status_code=404, detail="Module not found.")
    return module


@router.get("", response_model=list[ModuleSummary])
def list_modules(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User | None, Depends(get_optional_user)],
) -> list[dict]:
    modules = db.scalars(select(SkillModule).order_by(SkillModule.code)).all()
    done = completions_by_module(db, user.id) if user else {}
    return [present_module_summary(module, done.get(module.id)) for module in modules]


@router.get("/{code}", response_model=ModuleDetail)
def get_module(
    code: str,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User | None, Depends(get_optional_user)],
) -> dict:
    module = _get_module(db, code)
    completion = completion_for(db, user.id, module.id) if user else None
    missing: list[str] = []
    if user is not None and user.role == "learner":
        done = completed_codes(db, user.id)
        missing = [item for item in (module.prerequisites or []) if item not in done]
    return present_module_detail(module, completion, missing)


@router.post("/{code}/complete", response_model=CompletionResult)
def complete_module(
    code: str,
    body: CompleteModuleIn,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> dict:
    if user.role != "learner":
        raise HTTPException(status_code=403, detail="Only learners record module completions.")
    module = _get_module(db, code)
    existing = completion_for(db, user.id, module.id)
    if existing is not None:
        return {
            "code": module.code,
            "title": module.title,
            "completed_at": existing.completed_at.isoformat(),
            "already_completed": True,
            "passport_slug": user.slug,
        }
    done = completed_codes(db, user.id)
    missing = [item for item in (module.prerequisites or []) if item not in done]
    if missing:
        raise HTTPException(
            status_code=400,
            detail="Complete prerequisite modules first: " + ", ".join(missing),
        )
    checklist = list(module.checklist or [])
    if len(body.checked) != len(checklist) or not all(body.checked):
        raise HTTPException(status_code=400, detail="Confirm every self-check item to record this module.")
    completion = ModuleCompletion(
        user_id=user.id,
        module_id=module.id,
        checked=list(body.checked),
        completed_at=utcnow(),
    )
    db.add(completion)
    db.commit()
    db.refresh(completion)
    return {
        "code": module.code,
        "title": module.title,
        "completed_at": completion.completed_at.isoformat(),
        "already_completed": False,
        "passport_slug": user.slug,
    }
