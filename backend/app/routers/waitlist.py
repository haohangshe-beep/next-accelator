from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import WaitlistEntry, utcnow
from app.schemas import WaitlistIn, WaitlistOut

router = APIRouter(prefix="/waitlist", tags=["waitlist"])


@router.post("", response_model=WaitlistOut)
def join_waitlist(body: WaitlistIn, db: Annotated[Session, Depends(get_db)]) -> dict:
    existing = db.scalar(
        select(WaitlistEntry).where(WaitlistEntry.email == body.email, WaitlistEntry.topic == body.topic)
    )
    if existing is not None:
        return {"recorded": True, "already_registered": True}
    db.add(WaitlistEntry(email=body.email, topic=body.topic, created_at=utcnow()))
    db.commit()
    return {"recorded": True, "already_registered": False}
