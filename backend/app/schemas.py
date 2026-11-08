from __future__ import annotations

import re
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

CODE_PATTERN = re.compile(r"^[A-Z]{2,6}[0-9]{3}$")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class TrackCode(str, Enum):
    AI = "AI"
    NewSpace = "NewSpace"
    Robotics = "Robotics"
    LowAltitude = "LowAltitude"


Level = Literal["Foundation", "Intermediate", "Advanced"]
Difficulty = Literal["Introductory", "Intermediate", "Advanced"]


def _items(
    values: list[str],
    *,
    label: str,
    min_count: int,
    max_count: int,
    min_len: int,
    max_len: int,
) -> list[str]:
    cleaned: list[str] = []
    for item in values:
        text = " ".join(str(item).split())
        if not text:
            continue
        if len(text) < min_len or len(text) > max_len:
            raise ValueError(f"Each {label} must be between {min_len} and {max_len} characters.")
        cleaned.append(text)
    if len(cleaned) < min_count:
        raise ValueError(f"Add at least {min_count} {label}.")
    if len(cleaned) > max_count:
        raise ValueError(f"Use at most {max_count} {label}.")
    return cleaned


def _codes(values: list[str]) -> list[str]:
    cleaned: list[str] = []
    for item in values:
        code = str(item).strip().upper()
        if not code:
            continue
        if not CODE_PATTERN.fullmatch(code):
            raise ValueError(f"{item} is not a module code such as AI101.")
        if code not in cleaned:
            cleaned.append(code)
    return cleaned


class LoginIn(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class ModuleWrite(BaseModel):
    title: str = Field(min_length=3, max_length=160)
    track: TrackCode
    level: Level
    summary: str = Field(min_length=10, max_length=2000)
    learning_outcomes: list[str]
    estimated_hours: int = Field(ge=1, le=80)
    prerequisites: list[str] = []
    checklist: list[str]

    @field_validator("title", "summary")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()

    @field_validator("learning_outcomes")
    @classmethod
    def outcomes_ok(cls, values: list[str]) -> list[str]:
        return _items(values, label="learning outcome", min_count=1, max_count=8, min_len=8, max_len=240)

    @field_validator("checklist")
    @classmethod
    def checklist_ok(cls, values: list[str]) -> list[str]:
        return _items(values, label="self-check item", min_count=1, max_count=8, min_len=8, max_len=240)

    @field_validator("prerequisites")
    @classmethod
    def prerequisites_ok(cls, values: list[str]) -> list[str]:
        return _codes(values)


class ModuleCreate(ModuleWrite):
    code: str

    @field_validator("code", mode="before")
    @classmethod
    def code_ok(cls, value: object) -> object:
        if not isinstance(value, str):
            return value
        code = value.strip().upper()
        if not CODE_PATTERN.fullmatch(code):
            raise ValueError("Use a code such as AI101.")
        return code


class MissionCreate(BaseModel):
    title: str = Field(min_length=4, max_length=140)
    track: TrackCode
    difficulty: Difficulty
    summary: str = Field(min_length=10, max_length=2000)
    problem_statement: str = Field(min_length=20, max_length=8000)
    deliverables: str = Field(min_length=10, max_length=4000)
    required_skill_codes: list[str] = []
    suggested_competencies: list[str] = []
    deadline: str | None = None

    @field_validator("title", "summary", "problem_statement", "deliverables")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()

    @field_validator("required_skill_codes")
    @classmethod
    def skills_ok(cls, values: list[str]) -> list[str]:
        return _codes(values)

    @field_validator("suggested_competencies")
    @classmethod
    def competencies_ok(cls, values: list[str]) -> list[str]:
        return _items(values, label="competency", min_count=0, max_count=8, min_len=2, max_len=60)

    @field_validator("deadline")
    @classmethod
    def deadline_ok(cls, value: str | None) -> str | None:
        if value is None or value == "":
            return None
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            raise ValueError("Use a deadline in YYYY-MM-DD format.")
        return value


class CompleteModuleIn(BaseModel):
    checked: list[bool]


class SubmitIn(BaseModel):
    deliverable_url: str
    notes: str

    @field_validator("deliverable_url")
    @classmethod
    def url_ok(cls, value: str) -> str:
        text = value.strip()
        if not (text.startswith("http://") or text.startswith("https://")):
            raise ValueError("Deliverable URL must start with http:// or https://")
        if len(text) > 500:
            raise ValueError("URL is too long.")
        return text

    @field_validator("notes")
    @classmethod
    def notes_ok(cls, value: str) -> str:
        text = value.strip()
        if len(text) < 1:
            raise ValueError("Add a short note about the evidence.")
        if len(text) > 4000:
            raise ValueError("Notes are too long.")
        return text


class ReviewIn(BaseModel):
    action: Literal["approve", "request_changes"]
    competency_tags: list[str] = []
    feedback: str = ""

    @field_validator("feedback")
    @classmethod
    def feedback_ok(cls, value: str) -> str:
        return value.strip()


class WaitlistIn(BaseModel):
    email: str
    topic: Literal["talent", "apprenticeships"]

    @field_validator("email")
    @classmethod
    def email_ok(cls, value: str) -> str:
        text = value.strip().lower()
        if not EMAIL_PATTERN.fullmatch(text):
            raise ValueError("Enter a valid email address.")
        return text


class OrganizationOut(BaseModel):
    id: int
    name: str
    summary: str


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    slug: str
    headline: str
    bio: str
    interests: list[str]
    organization: OrganizationOut | None


class TokenOut(BaseModel):
    access_token: str
    token_type: str
    user: UserOut


class ModuleSummary(BaseModel):
    code: str
    title: str
    track: str
    level: str
    summary: str
    estimated_hours: int
    prerequisites: list[str]
    completed: bool
    completed_at: str | None


class ModuleDetail(ModuleSummary):
    learning_outcomes: list[str]
    checklist: list[str]
    missing_prerequisites: list[str]


class CompletionResult(BaseModel):
    code: str
    title: str
    completed_at: str
    already_completed: bool
    passport_slug: str


class CertificationOut(BaseModel):
    id: int
    mission_id: int
    mission_title: str
    organization_name: str
    issuer_name: str
    competency_tags: list[str]
    statement: str
    issued_at: str


class SubmissionOut(BaseModel):
    id: int
    mission_id: int
    mission_title: str
    mission_track: str
    organization_name: str
    status: str
    deliverable_url: str
    notes: str
    feedback: str
    learner_name: str
    learner_slug: str
    created_at: str
    updated_at: str
    can_review: bool
    suggested_competencies: list[str]
    certification: CertificationOut | None


class MissionSummary(BaseModel):
    id: int
    title: str
    organization_name: str
    track: str
    difficulty: str
    summary: str
    required_skill_codes: list[str]
    deadline: str | None
    status: str
    membership_status: str | None


class MissionDetail(MissionSummary):
    problem_statement: str
    deliverables: str
    suggested_competencies: list[str]
    missing_skill_codes: list[str]
    my_submission: SubmissionOut | None
    submissions: list[SubmissionOut]


class ReviewResult(BaseModel):
    submission: SubmissionOut
    certification: CertificationOut | None


class PassportProfile(BaseModel):
    full_name: str
    slug: str
    headline: str
    bio: str
    interests: list[str]


class PassportModule(BaseModel):
    code: str
    title: str
    track: str
    level: str
    estimated_hours: int
    completed_at: str


class PassportMission(BaseModel):
    id: int
    title: str
    track: str
    organization_name: str
    status: str
    deliverable_url: str | None
    joined_at: str


class PassportOut(BaseModel):
    profile: PassportProfile
    modules: list[PassportModule]
    missions: list[PassportMission]
    certifications: list[CertificationOut]


class RecommendationOut(BaseModel):
    id: str
    kind: Literal["module", "mission", "passport", "submission"]
    title: str
    reason: str
    action_label: str
    href: str


class NavigatorOut(BaseModel):
    summary: str
    recommendations: list[RecommendationOut]


class LearnerSubmissionRef(BaseModel):
    id: int
    mission_id: int
    mission_title: str
    status: str
    updated_at: str


class LearnerHome(BaseModel):
    completed_modules: int
    missions_joined: int
    certifications: int
    passport_slug: str
    submissions: list[LearnerSubmissionRef]


class EmployerMissionRef(BaseModel):
    id: int
    title: str
    track: str
    status: str
    submission_count: int
    pending_count: int


class PendingReview(BaseModel):
    id: int
    mission_id: int
    mission_title: str
    learner_name: str
    learner_slug: str
    submitted_at: str


class EmployerHome(BaseModel):
    organization_name: str
    missions: list[EmployerMissionRef]
    pending_reviews: list[PendingReview]


class AdminHome(BaseModel):
    module_count: int
    mission_count: int
    user_count: int
    waitlist_count: int


class DashboardOut(BaseModel):
    user: UserOut
    learner: LearnerHome | None
    employer: EmployerHome | None
    admin: AdminHome | None


class TrackOut(BaseModel):
    code: str
    label: str


class WaitlistOut(BaseModel):
    recorded: bool
    already_registered: bool


class MessageOut(BaseModel):
    model_config = ConfigDict(extra="ignore")
    status: str = "ok"
