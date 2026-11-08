"""Portable relational schema.

SQLite is the demo default. Column types stay in the SQLAlchemy portable set,
JSON becomes JSONB under PostgreSQL, and timestamps are timezone-aware. Switch
the database by setting FTOS_DATABASE_URL; create_all builds this schema on startup.
"""

from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import JSON, CheckConstraint, Date, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from app.tracks import (
    DIFFICULTIES,
    LEVELS,
    MEMBERSHIP_STATUSES,
    MISSION_STATUSES,
    ROLES,
    SUBMISSION_STATUSES,
    TRACK_LABELS,
    WAITLIST_TOPICS,
    in_check,
)

PortableJSON = JSON().with_variant(JSONB(), "postgresql")


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    summary: Mapped[str] = mapped_column(Text, default="", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    members: Mapped[list[User]] = relationship(back_populates="organization")
    missions: Mapped[list[Mission]] = relationship(back_populates="organization")


class User(Base):
    __tablename__ = "users"
    __table_args__ = (CheckConstraint(in_check("role", ROLES), name="ck_users_role"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    headline: Mapped[str] = mapped_column(String(240), default="", nullable=False)
    bio: Mapped[str] = mapped_column(Text, default="", nullable=False)
    interests: Mapped[list[str]] = mapped_column(PortableJSON, default=list, nullable=False)
    organization_id: Mapped[int | None] = mapped_column(ForeignKey("organizations.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    organization: Mapped[Organization | None] = relationship(back_populates="members")


class SkillModule(Base):
    __tablename__ = "skill_modules"
    __table_args__ = (
        CheckConstraint(in_check("track", tuple(TRACK_LABELS)), name="ck_skill_modules_track"),
        CheckConstraint(in_check("level", LEVELS), name="ck_skill_modules_level"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(16), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    track: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    level: Mapped[str] = mapped_column(String(20), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    learning_outcomes: Mapped[list[str]] = mapped_column(PortableJSON, default=list, nullable=False)
    estimated_hours: Mapped[int] = mapped_column(nullable=False)
    prerequisites: Mapped[list[str]] = mapped_column(PortableJSON, default=list, nullable=False)
    checklist: Mapped[list[str]] = mapped_column(PortableJSON, default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)


class ModuleCompletion(Base):
    __tablename__ = "module_completions"
    __table_args__ = (
        UniqueConstraint("user_id", "module_id", name="uq_module_completions_user_module"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    module_id: Mapped[int] = mapped_column(ForeignKey("skill_modules.id"), nullable=False, index=True)
    checked: Mapped[list[bool]] = mapped_column(PortableJSON, default=list, nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    module: Mapped[SkillModule] = relationship()
    user: Mapped[User] = relationship()


class Mission(Base):
    __tablename__ = "missions"
    __table_args__ = (
        CheckConstraint(in_check("track", tuple(TRACK_LABELS)), name="ck_missions_track"),
        CheckConstraint(in_check("difficulty", DIFFICULTIES), name="ck_missions_difficulty"),
        CheckConstraint(in_check("status", MISSION_STATUSES), name="ck_missions_status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    track: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    problem_statement: Mapped[str] = mapped_column(Text, nullable=False)
    deliverables: Mapped[str] = mapped_column(Text, nullable=False)
    required_skill_codes: Mapped[list[str]] = mapped_column(PortableJSON, default=list, nullable=False)
    suggested_competencies: Mapped[list[str]] = mapped_column(PortableJSON, default=list, nullable=False)
    deadline: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="open", nullable=False)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    organization: Mapped[Organization] = relationship(back_populates="missions")
    author: Mapped[User] = relationship(foreign_keys="Mission.created_by")


class MissionMembership(Base):
    __tablename__ = "mission_memberships"
    __table_args__ = (
        UniqueConstraint("mission_id", "user_id", name="uq_memberships_mission_user"),
        CheckConstraint(in_check("status", MEMBERSHIP_STATUSES), name="ck_memberships_status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    mission_id: Mapped[int] = mapped_column(ForeignKey("missions.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), default="joined", nullable=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    mission: Mapped[Mission] = relationship()
    user: Mapped[User] = relationship()


class Submission(Base):
    __tablename__ = "submissions"
    __table_args__ = (
        UniqueConstraint("mission_id", "user_id", name="uq_submissions_mission_user"),
        CheckConstraint(in_check("status", SUBMISSION_STATUSES), name="ck_submissions_status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    mission_id: Mapped[int] = mapped_column(ForeignKey("missions.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    deliverable_url: Mapped[str] = mapped_column(String(500), nullable=False)
    notes: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False, index=True)
    feedback: Mapped[str] = mapped_column(Text, default="", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    mission: Mapped[Mission] = relationship()
    user: Mapped[User] = relationship()


class Certification(Base):
    __tablename__ = "certifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    submission_id: Mapped[int] = mapped_column(ForeignKey("submissions.id"), unique=True, nullable=False)
    mission_id: Mapped[int] = mapped_column(ForeignKey("missions.id"), nullable=False)
    issuer_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    issuer_name: Mapped[str] = mapped_column(String(200), nullable=False)
    organization_name: Mapped[str] = mapped_column(String(200), nullable=False)
    competency_tags: Mapped[list[str]] = mapped_column(PortableJSON, default=list, nullable=False)
    statement: Mapped[str] = mapped_column(Text, nullable=False)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    learner: Mapped[User] = relationship(foreign_keys="Certification.user_id")
    mission: Mapped[Mission] = relationship()
    submission: Mapped[Submission] = relationship()


class WaitlistEntry(Base):
    __tablename__ = "waitlist_entries"
    __table_args__ = (
        UniqueConstraint("email", "topic", name="uq_waitlist_email_topic"),
        CheckConstraint(in_check("topic", WAITLIST_TOPICS), name="ck_waitlist_topic"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    topic: Mapped[str] = mapped_column(String(40), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
