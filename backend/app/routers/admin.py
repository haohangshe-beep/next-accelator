from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_roles
from app.models import Mission, ModuleCompletion, SkillModule, User, utcnow
from app.present import present_module_detail
from app.schemas import ModuleCreate, ModuleDetail, ModuleWrite

router = APIRouter(prefix="/admin", tags=["admin"])


def _module(db: Session, code: str) -> SkillModule:
    module = db.scalar(select(SkillModule).where(SkillModule.code == code.strip().upper()))
    if module is None:
        raise HTTPException(status_code=404, detail="Module not found.")
    return module


def _assert_prerequisites(db: Session, code: str, prerequisites: list[str]) -> None:
    if code in prerequisites:
        raise HTTPException(status_code=400, detail="A module cannot list itself as a prerequisite.")
    if prerequisites:
        found = set(db.scalars(select(SkillModule.code).where(SkillModule.code.in_(prerequisites))).all())
        missing = [item for item in prerequisites if item not in found and item != code]
        if missing:
            raise HTTPException(status_code=400, detail="Unknown prerequisite codes: " + ", ".join(missing))
    graph = {module.code: list(module.prerequisites or []) for module in db.scalars(select(SkillModule)).all()}
    graph[code] = list(prerequisites)
    visiting: set[str] = set()

    def visit(node: str) -> None:
        if node in visiting:
            raise HTTPException(status_code=400, detail="Prerequisites cannot form a cycle.")
        if node not in graph:
            return
        visiting.add(node)
        for nxt in graph[node]:
            visit(nxt)
        visiting.remove(node)
        graph.pop(node, None)

    visit(code)


def _apply(module: SkillModule, body: ModuleWrite) -> None:
    module.title = body.title
    module.track = body.track.value
    module.level = body.level
    module.summary = body.summary
    module.learning_outcomes = body.learning_outcomes
    module.estimated_hours = body.estimated_hours
    module.prerequisites = body.prerequisites
    module.checklist = body.checklist


@router.post("/modules", response_model=ModuleDetail, status_code=201)
def create_module(
    body: ModuleCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles("admin"))],
) -> dict:
    if db.scalar(select(SkillModule.id).where(SkillModule.code == body.code)):
        raise HTTPException(status_code=409, detail="A module with this code already exists.")
    _assert_prerequisites(db, body.code, body.prerequisites)
    module = SkillModule(
        code=body.code,
        title=body.title,
        track=body.track.value,
        level=body.level,
        summary=body.summary,
        learning_outcomes=body.learning_outcomes,
        estimated_hours=body.estimated_hours,
        prerequisites=body.prerequisites,
        checklist=body.checklist,
        created_at=utcnow(),
    )
    db.add(module)
    db.commit()
    db.refresh(module)
    return present_module_detail(module, None)


@router.put("/modules/{code}", response_model=ModuleDetail)
def update_module(
    code: str,
    body: ModuleWrite,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles("admin"))],
) -> dict:
    module = _module(db, code)
    _assert_prerequisites(db, module.code, body.prerequisites)
    _apply(module, body)
    db.commit()
    db.refresh(module)
    return present_module_detail(module, None)


@router.delete("/modules/{code}", status_code=204)
def delete_module(
    code: str,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles("admin"))],
) -> None:
    module = _module(db, code)
    if db.scalar(select(ModuleCompletion.id).where(ModuleCompletion.module_id == module.id)):
        raise HTTPException(status_code=409, detail="Learners have already completed this module.")
    others = db.scalars(select(SkillModule).where(SkillModule.code != module.code)).all()
    if any(module.code in (item.prerequisites or []) for item in others):
        raise HTTPException(status_code=409, detail="Another module lists this code as a prerequisite.")
    missions = db.scalars(select(Mission)).all()
    if any(module.code in (mission.required_skill_codes or []) for mission in missions):
        raise HTTPException(status_code=409, detail="A mission still requires this module.")
    db.delete(module)
    db.commit()
