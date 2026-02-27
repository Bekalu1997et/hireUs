"""
Seed initial data for local development.

Run:
  cd backend
  python scripts/seed.py
"""
from __future__ import annotations

import asyncio
import sys
import uuid
from datetime import datetime
from pathlib import Path

from sqlalchemy import select

# Ensure backend root is importable when running `python scripts/seed.py`.
BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.config import settings
from app.core.security import get_password_hash
from app.db import models as _models  # noqa: F401 - ensure mappers are registered
from app.db.models import InterviewKit, Organization, Role, User, UserRole, Workflow
from app.db.session import AsyncSessionLocal


async def _get_or_create_superuser(session) -> User:
    result = await session.execute(
        select(User).where(User.email == settings.FIRST_SUPERUSER_EMAIL.lower())
    )
    user = result.scalar_one_or_none()
    if user:
        print(f"= Superuser exists: {user.email}")
        return user

    user = User(
        id=str(uuid.uuid4()),
        email=settings.FIRST_SUPERUSER_EMAIL.lower(),
        hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
        full_name="Admin User",
        role=UserRole.SUPERADMIN,
        is_superuser=True,
        is_active=True,
        email_verified=True,
        created_at=datetime.utcnow(),
    )
    session.add(user)
    await session.flush()
    print(f"+ Created superuser: {user.email}")
    return user


async def _get_or_create_organization(session) -> Organization:
    result = await session.execute(
        select(Organization).where(Organization.slug == "acme-corp")
    )
    org = result.scalar_one_or_none()
    if org:
        print(f"= Organization exists: {org.name}")
        return org

    org = Organization(
        id=str(uuid.uuid4()),
        name="Acme Corporation",
        slug="acme-corp",
        description="A sample organization for local development",
        industry="Technology",
        size="50-200",
        is_active=True,
        created_at=datetime.utcnow(),
    )
    session.add(org)
    await session.flush()
    print(f"+ Created organization: {org.name}")
    return org


async def _create_roles(session, org_id: str, created_by: str | None) -> None:
    roles_data = [
        {
            "slug": "senior-python-developer",
            "title": "Senior Python Developer",
            "description": "Build scalable backend services.",
            "department": "Engineering",
            "seniority": "Senior",
            "tech_stack": ["Python", "FastAPI", "PostgreSQL", "Docker"],
            "core_competencies": ["Problem Solving", "System Design", "Code Quality"],
            "mission": "Build high-performance APIs",
        },
        {
            "slug": "frontend-engineer",
            "title": "Frontend Engineer",
            "description": "Create robust user interfaces.",
            "department": "Engineering",
            "seniority": "Mid-Level",
            "tech_stack": ["React", "Next.js", "TypeScript", "Tailwind"],
            "core_competencies": ["UI/UX", "Component Design", "State Management"],
            "mission": "Deliver exceptional user experiences",
        },
    ]

    created = 0
    for data in roles_data:
        exists = await session.execute(
            select(Role).where(
                Role.organization_id == org_id,
                Role.slug == data["slug"],
            )
        )
        if exists.scalar_one_or_none():
            continue

        role = Role(
            id=str(uuid.uuid4()),
            organization_id=org_id,
            created_by=created_by,
            is_active=True,
            created_at=datetime.utcnow(),
            **data,
        )
        session.add(role)
        created += 1

    if created:
        print(f"+ Created {created} roles")
    else:
        print("= Roles already seeded")


async def _create_workflow(session, org_id: str, created_by: str | None) -> None:
    result = await session.execute(
        select(Workflow).where(
            Workflow.organization_id == org_id,
            Workflow.name == "Standard Interview Pipeline",
        )
    )
    if result.scalar_one_or_none():
        print("= Workflow already seeded")
        return

    workflow = Workflow(
        id=str(uuid.uuid4()),
        organization_id=org_id,
        name="Standard Interview Pipeline",
        description="Default hiring workflow",
        stages=[
            {"id": "1", "name": "Applied", "color": "#6B7280"},
            {"id": "2", "name": "Screening", "color": "#3B82F6"},
            {"id": "3", "name": "Technical Interview", "color": "#8B5CF6"},
            {"id": "4", "name": "Culture Fit", "color": "#10B981"},
            {"id": "5", "name": "Offer", "color": "#F59E0B"},
            {"id": "6", "name": "Hired", "color": "#22C55E"},
        ],
        is_default=True,
        is_active=True,
        created_by=created_by,
        created_at=datetime.utcnow(),
    )
    session.add(workflow)
    print("+ Created workflow: Standard Interview Pipeline")


async def _create_interview_kits(session, org_id: str, created_by: str | None) -> None:
    kits_data = [
        {
            "title": "Python Technical Interview",
            "type": "coding",
            "description": "Assess Python programming skills.",
            "estimated_duration_minutes": 60,
            "questions": [
                "Explain list vs tuple in Python.",
                "How does Python garbage collection work?",
                "Implement a function to reverse a string.",
            ],
        },
        {
            "title": "System Design Discussion",
            "type": "system_design",
            "description": "Evaluate system design skills.",
            "estimated_duration_minutes": 45,
            "questions": [
                "Design a URL shortener service.",
                "How would you design a chat application?",
            ],
        },
    ]

    created = 0
    for data in kits_data:
        exists = await session.execute(
            select(InterviewKit).where(
                InterviewKit.organization_id == org_id,
                InterviewKit.title == data["title"],
            )
        )
        if exists.scalar_one_or_none():
            continue

        kit = InterviewKit(
            id=str(uuid.uuid4()),
            organization_id=org_id,
            created_by=created_by,
            is_active=True,
            is_template=True,
            version=1,
            created_at=datetime.utcnow(),
            **data,
        )
        session.add(kit)
        created += 1

    if created:
        print(f"+ Created {created} interview kits")
    else:
        print("= Interview kits already seeded")


async def seed() -> None:
    async with AsyncSessionLocal() as session:
        admin = await _get_or_create_superuser(session)
        org = await _get_or_create_organization(session)
        await _create_roles(session, org.id, admin.id if admin else None)
        await _create_workflow(session, org.id, admin.id if admin else None)
        await _create_interview_kits(session, org.id, admin.id if admin else None)
        await session.commit()
    print("\nSeed completed.")


if __name__ == "__main__":
    asyncio.run(seed())
