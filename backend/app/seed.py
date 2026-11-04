"""Demo catalogue, accounts, and one submission waiting for employer certification."""

from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Mission, MissionMembership, ModuleCompletion, Organization, SkillModule, Submission, User
from app.security import hash_password

DEMO_PASSWORD = "demo-ftos-2026"


def _at(year: int, month: int, day: int, hour: int = 9) -> datetime:
    return datetime(year, month, day, hour, 0, tzinfo=timezone.utc)


MODULES: list[dict] = [
    {
        "code": "AI101",
        "title": "Foundations of Applied AI",
        "track": "AI",
        "level": "Foundation",
        "estimated_hours": 6,
        "prerequisites": [],
        "summary": "Frame, evaluate, and explain a first applied-AI use case in a Hong Kong organisation.",
        "learning_outcomes": [
            "Frame an industry problem as prediction, classification, or assistance",
            "Describe data, a model, and an evaluation metric in plain language",
            "Name one privacy or bias risk and a practical mitigation",
        ],
        "checklist": [
            "I can tell a supervised-learning task from a rules-only workflow",
            "I can name the data I would need for a weekly harbour-logistics forecast",
            "I can list one risk and one mitigation for a public-facing assistant",
        ],
    },
    {
        "code": "AI102",
        "title": "Applied AI for Operations",
        "track": "AI",
        "level": "Intermediate",
        "estimated_hours": 8,
        "prerequisites": ["AI101"],
        "summary": "Turn a use case into an operations workflow with a metric, a human review step, and a one-page model card.",
        "learning_outcomes": [
            "Define a success metric an operations lead would accept",
            "Design a human-in-the-loop review step",
            "Write a one-page model card another team can audit",
        ],
        "checklist": [
            "I can define one metric and the decision it should change",
            "I can point to where a person reviews the model before it acts",
            "I can draft a model card with purpose, data, limits, and an owner",
        ],
    },
    {
        "code": "PE101",
        "title": "Payload Engineering Basics",
        "track": "NewSpace",
        "level": "Foundation",
        "estimated_hours": 6,
        "prerequisites": [],
        "summary": "Specify, test, and monitor a small-satellite payload the way a Hong Kong NewSpace supplier would hand it to a bus team.",
        "learning_outcomes": [
            "Read a simple payload specification and list the interfaces that matter",
            "Describe a ground-test check before flight",
            "Outline a health metric a student CubeSat team could log each pass",
        ],
        "checklist": [
            "I can name three payload interfaces such as power, data, or thermal",
            "I can explain one test I would run before integrating with a bus",
            "I can define a health metric and the threshold that needs a human look",
        ],
    },
    {
        "code": "CV101",
        "title": "Computer Vision for Field Systems",
        "track": "Robotics",
        "level": "Foundation",
        "estimated_hours": 7,
        "prerequisites": [],
        "summary": "Plan a camera, a small dataset, and an evaluation for inspection or picking tasks in a real workspace.",
        "learning_outcomes": [
            "Choose a camera placement and a lighting constraint for a field task",
            "Describe how you would collect and label a starter dataset",
            "Define a success metric and a failure case the operator must still catch",
        ],
        "checklist": [
            "I can sketch where a camera sits for a picking or inspection task",
            "I can list what I would label and what I would leave to a person",
            "I can name one failure mode and how the operator would notice it",
        ],
    },
    {
        "code": "DO101",
        "title": "Drone Operations Fundamentals",
        "track": "LowAltitude",
        "level": "Foundation",
        "estimated_hours": 6,
        "prerequisites": [],
        "summary": "Plan a safety-first drone task in Hong Kong's low-altitude economy, including airspace awareness and an evidence pack.",
        "learning_outcomes": [
            "Build a pre-flight checklist for a survey task",
            "Identify airspace, weather, and privacy constraints to check before flying",
            "Package photos, logs, and notes a client can audit",
        ],
        "checklist": [
            "I can write a pre-flight checklist with weather, battery, and site items",
            "I can name two constraints I would check before a New Territories survey",
            "I can list the evidence I would hand a client after the flight",
        ],
    },
]


MISSIONS: list[dict] = [
    {
        "title": "Port Community Demand Forecast",
        "track": "AI",
        "difficulty": "Intermediate",
        "required_skill_codes": ["AI101"],
        "deadline": date(2026, 12, 18),
        "summary": "Forecast weekly barge demand for a mid-stream operator and show the error honestly.",
        "problem_statement": (
            "A mid-stream operator on Victoria Harbour still plans crew from last month's average. "
            "They want a weekly forecast they can compare with a naive baseline, plus a note on when not to trust it."
        ),
        "deliverables": (
            "A link to a notebook, report, or slides. Include the metric (MAE or one you can justify), "
            "the baseline, and a short limits section."
        ),
        "suggested_competencies": ["Demand forecasting", "Metric design", "Applied AI communication"],
    },
    {
        "title": "Bilingual Service Triage Brief",
        "track": "AI",
        "difficulty": "Advanced",
        "required_skill_codes": ["AI101", "AI102"],
        "deadline": date(2027, 1, 29),
        "summary": "Design a human-reviewed triage flow for bilingual walk-in enquiries at a neighbourhood services centre.",
        "problem_statement": (
            "Staff lose time routing repeat questions in Cantonese and English. They will not accept a chatbot "
            "that answers the public on its own. They want a triage brief: categories, a confidence rule, and the handoff to a person."
        ),
        "deliverables": (
            "A link to a two-page brief. Cover categories, the review step, a metric, and what the system must refuse to answer."
        ),
        "suggested_competencies": ["Workflow design", "Human-in-the-loop review", "Model documentation"],
    },
    {
        "title": "CubeSat Payload Health Log",
        "track": "NewSpace",
        "difficulty": "Intermediate",
        "required_skill_codes": ["PE101"],
        "deadline": date(2027, 2, 12),
        "summary": "Propose a health-log template a university CubeSat team can fill in after each pass.",
        "problem_statement": (
            "A campus team flies a small imaging payload and stores screenshots in a shared drive. Mentors cannot see "
            "which passes were healthy. They want a template and a threshold that triggers a human look."
        ),
        "deliverables": (
            "A link to the template plus a half-page note on the metric, the threshold, and the test you would run before flight."
        ),
        "suggested_competencies": ["Payload health monitoring", "Test planning", "Technical writing"],
    },
    {
        "title": "Warehouse Picking Vision Trial",
        "track": "Robotics",
        "difficulty": "Intermediate",
        "required_skill_codes": ["CV101"],
        "deadline": date(2027, 1, 15),
        "summary": "Write an evaluation protocol for a camera-based picking assistant in a Tsuen Wan warehouse.",
        "problem_statement": (
            "A third-party logistics team is piloting a camera that suggests the next pick. Misses are expensive, and "
            "the night shift does not trust a demo video. They want a trial protocol, not a model."
        ),
        "deliverables": (
            "A link to the protocol: camera placement, what you label, the success metric, and the cases an operator must still catch."
        ),
        "suggested_competencies": ["Evaluation design", "Field robotics", "Operator handoff"],
    },
    {
        "title": "Country Park Corridor Survey Plan",
        "track": "LowAltitude",
        "difficulty": "Introductory",
        "required_skill_codes": ["DO101"],
        "deadline": date(2026, 12, 30),
        "summary": "Plan a drone survey of slope conditions along a New Territories access road.",
        "problem_statement": (
            "A facilities contractor walks a slope road after heavy rain. They want a drone plan that a pilot could fly "
            "and an evidence pack a supervisor could file. This mission is a plan, not a flight."
        ),
        "deliverables": (
            "A link to the survey plan: site constraints, pre-flight checklist, data you will capture, and how you will name the files."
        ),
        "suggested_competencies": ["Mission planning", "Low-altitude safety", "Evidence packaging"],
    },
    {
        "title": "SME Grant Narrative Assistant",
        "track": "AI",
        "difficulty": "Introductory",
        "required_skill_codes": ["AI101"],
        "deadline": None,
        "summary": "Turn rough technical notes into a two-page innovation-grant narrative for a Science Park startup.",
        "problem_statement": (
            "A two-person startup has strong notes and a weak narrative. Reviewers keep asking what decision the model changes. "
            "They want a draft they can edit, with one metric and one limit stated in plain language."
        ),
        "deliverables": (
            "A link to the two-page draft. Keep their technical claims, add the metric, and mark anything you had to assume."
        ),
        "suggested_competencies": ["Technical storytelling", "Metric design", "Applied AI communication"],
    },
]


def seed(db: Session) -> None:
    existing = db.scalar(select(User.id).where(User.email == "learner@demo.ftos"))
    if existing is not None:
        return

    organization = Organization(
        name="Harbour Frontier Labs",
        summary=(
            "A Hong Kong studio that runs short industry missions in applied AI, small-satellite payloads, "
            "field robotics, and low-altitude inspection."
        ),
        created_at=_at(2026, 8, 1),
    )
    db.add(organization)
    db.flush()

    password_hash = hash_password(DEMO_PASSWORD)
    learner = User(
        email="learner@demo.ftos",
        password_hash=password_hash,
        full_name="Alex Chen",
        role="learner",
        slug="alex-chen",
        headline="Career switcher building evidence in applied AI and field robotics.",
        bio=(
            "Based in Hong Kong. Building a public record of applied AI work and field robotics that an employer can check."
        ),
        interests=["AI", "Robotics"],
        organization_id=None,
        created_at=_at(2026, 9, 1),
    )
    employer = User(
        email="employer@demo.ftos",
        password_hash=password_hash,
        full_name="Jordan Lam",
        role="employer",
        slug="jordan-lam",
        headline="Mission lead at Harbour Frontier Labs.",
        bio="Publishes short industry missions and certifies the competencies a submission actually demonstrates.",
        interests=[],
        organization_id=organization.id,
        created_at=_at(2026, 8, 2),
    )
    admin = User(
        email="admin@demo.ftos",
        password_hash=password_hash,
        full_name="Sam Wu",
        role="admin",
        slug="sam-wu",
        headline="FTOS programme admin.",
        bio="Seeds skill modules and keeps the demo catalogue accurate.",
        interests=[],
        organization_id=None,
        created_at=_at(2026, 8, 2, 10),
    )
    db.add_all([learner, employer, admin])
    db.flush()

    modules_by_code: dict[str, SkillModule] = {}
    for item in MODULES:
        module = SkillModule(
            code=item["code"],
            title=item["title"],
            track=item["track"],
            level=item["level"],
            summary=item["summary"],
            learning_outcomes=item["learning_outcomes"],
            estimated_hours=item["estimated_hours"],
            prerequisites=item["prerequisites"],
            checklist=item["checklist"],
            created_at=_at(2026, 8, 15),
        )
        db.add(module)
        modules_by_code[module.code] = module
    db.flush()

    ai101 = modules_by_code["AI101"]
    db.add(
        ModuleCompletion(
            user_id=learner.id,
            module_id=ai101.id,
            checked=[True, True, True],
            completed_at=_at(2026, 10, 2),
        )
    )

    missions_by_title: dict[str, Mission] = {}
    for item in MISSIONS:
        mission = Mission(
            title=item["title"],
            organization_id=organization.id,
            track=item["track"],
            difficulty=item["difficulty"],
            summary=item["summary"],
            problem_statement=item["problem_statement"],
            deliverables=item["deliverables"],
            required_skill_codes=item["required_skill_codes"],
            suggested_competencies=item["suggested_competencies"],
            deadline=item["deadline"],
            status="open",
            created_by=employer.id,
            created_at=_at(2026, 9, 12),
        )
        db.add(mission)
        missions_by_title[mission.title] = mission
    db.flush()

    forecast = missions_by_title["Port Community Demand Forecast"]
    db.add(
        MissionMembership(
            mission_id=forecast.id,
            user_id=learner.id,
            status="submitted",
            joined_at=_at(2026, 10, 12),
        )
    )
    db.add(
        Submission(
            mission_id=forecast.id,
            user_id=learner.id,
            deliverable_url="https://notes.demo.ftos/alex-chen/port-forecast",
            notes=(
                "Weekly barge forecast with a seasonal naive baseline. MAE is the metric. "
                "The limits section flags public holidays and typhoon weeks as out of scope for this first model."
            ),
            status="pending",
            feedback="",
            created_at=_at(2026, 10, 20),
            updated_at=_at(2026, 10, 20),
        )
    )
    db.commit()
