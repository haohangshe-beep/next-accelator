from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.present import present_passport
from app.schemas import PassportOut

router = APIRouter(prefix="/passport", tags=["passport"])


@router.get("/{slug}", response_model=PassportOut)
def get_passport(slug: str, db: Annotated[Session, Depends(get_db)]) -> dict:
    user = db.scalar(select(User).where(User.slug == slug.strip().lower()))
    if user is None:
        raise HTTPException(status_code=404, detail="No passport found for this link.")
    return present_passport(db, user)
