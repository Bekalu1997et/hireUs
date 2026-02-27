"""
Database models.
SQLAlchemy models for the application.
"""
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import List, Optional
from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, Text, 
    ForeignKey, Enum, Table, JSON, Index
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base


class UserRole(str, PyEnum):
    """
    User roles enumeration.
    """
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    RECRUITER = "recruiter"
    INTERVIEWER = "interviewer"
    HIRING_MANAGER = "hiring_manager"
    CANDIDATE = "candidate"


class OrganizationMemberRole(str, PyEnum):
    """
    Organization member role enumeration.
    """
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


def _enum_values(enum_cls):
    """Persist enum values (lowercase) instead of enum names."""
    return [item.value for item in enum_cls]


class User(Base):
    """
    User model for authentication and authorization.
    """
    __tablename__ = "users"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, values_callable=_enum_values),
        default=UserRole.INTERVIEWER,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )
    
    # Relationships
    organizations: Mapped[List["OrganizationMember"]] = relationship(
        "OrganizationMember",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    # Interviewer relationships
    interview_assignments: Mapped[List["InterviewAssignment"]] = relationship(
        "InterviewAssignment",
        back_populates="interviewer"
    )
    
    feedbacks: Mapped[List["Feedback"]] = relationship(
        "Feedback",
        back_populates="interviewer"
    )
    
    # Audit trail
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        "AuditLog",
        back_populates="user"
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"


class Organization(Base):
    """
    Organization model for multi-tenant support.
    """
    __tablename__ = "organizations"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    industry: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    size: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # e.g., "1-10", "11-50", etc.
    settings: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )
    
    # Relationships
    members: Mapped[List["OrganizationMember"]] = relationship(
        "OrganizationMember",
        back_populates="organization",
        cascade="all, delete-orphan"
    )
    roles: Mapped[List["Role"]] = relationship(
        "Role",
        back_populates="organization",
        cascade="all, delete-orphan"
    )
    candidates: Mapped[List["Candidate"]] = relationship(
        "Candidate",
        back_populates="organization",
        cascade="all, delete-orphan"
    )
    interview_kits: Mapped[List["InterviewKit"]] = relationship(
        "InterviewKit",
        back_populates="organization",
        cascade="all, delete-orphan"
    )
    workflows: Mapped[List["Workflow"]] = relationship(
        "Workflow",
        back_populates="organization",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Organization(id={self.id}, name={self.name}, slug={self.slug})>"


class OrganizationMember(Base):
    """
    Association table for users and organizations with roles.
    """
    __tablename__ = "organization_members"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    organization_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False
    )
    role: Mapped[OrganizationMemberRole] = mapped_column(
        Enum(OrganizationMemberRole, values_callable=_enum_values),
        default=OrganizationMemberRole.MEMBER
    )
    invited_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    accepted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    invited_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="organizations")
    organization: Mapped["Organization"] = relationship("Organization", back_populates="members")
    
    # Unique constraint to prevent duplicate memberships
    __table_args__ = (
        Index("ix_organization_members_user_org", "user_id", "organization_id", unique=True),
    )


class Role(Base):
    """
    Job role/position model.
    """
    __tablename__ = "roles"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    seniority: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # e.g., "Junior", "Senior", "Lead"
    department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tech_stack: Mapped[Optional[dict]] = mapped_column(JSON, default=list)  # e.g., ["Python", "React", "PostgreSQL"]
    core_competencies: Mapped[Optional[dict]] = mapped_column(JSON, default=list)  # AI-suggested competencies
    interview_stages: Mapped[Optional[dict]] = mapped_column(JSON, default=list)  # Suggested interview stages
    mission: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    must_have: Mapped[Optional[dict]] = mapped_column(JSON, default=list)
    nice_to_have: Mapped[Optional[dict]] = mapped_column(JSON, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="roles")
    candidates: Mapped[List["Candidate"]] = relationship(
        "Candidate",
        back_populates="role"
    )
    interview_kits: Mapped[List["InterviewKit"]] = relationship(
        "InterviewKit",
        back_populates="role"
    )
    
    def __repr__(self) -> str:
        return f"<Role(id={self.id}, title={self.title}, organization_id={self.organization_id})>"


class Candidate(Base):
    """
    Candidate model.
    """
    __tablename__ = "candidates"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False
    )
    role_id: Mapped[Optional[str]] = mapped_column(
        String(36), 
        ForeignKey("roles.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # Basic info
    email: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    resume_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    portfolio_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # AI-generated summary
    ai_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Workflow
    workflow_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("workflows.id"), nullable=True)
    current_stage_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    
    # Status
    status: Mapped[str] = mapped_column(String(50), default="applied")  # applied, screening, interview, offer, hired, rejected
    source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # linkedin, referral, direct, etc.
    
    # Metadata
    candidate_metadata: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="candidates")
    role: Mapped[Optional["Role"]] = relationship("Role", back_populates="candidates")
    interview_assignments: Mapped[List["InterviewAssignment"]] = relationship(
        "InterviewAssignment",
        back_populates="candidate"
    )
    feedbacks: Mapped[List["Feedback"]] = relationship(
        "Feedback",
        back_populates="candidate"
    )
    workflow: Mapped[Optional["Workflow"]] = relationship("Workflow", foreign_keys=[workflow_id])
    stage_history: Mapped[List["StageHistory"]] = relationship(
        "StageHistory",
        back_populates="candidate"
    )
    
    def __repr__(self) -> str:
        return f"<Candidate(id={self.id}, name={self.full_name}, email={self.email})>"


class InterviewKit(Base):
    """
    Interview kit model - contains questions, rubrics, and evaluation criteria.
    """
    __tablename__ = "interview_kits"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False
    )
    role_id: Mapped[Optional[str]] = mapped_column(
        String(36), 
        ForeignKey("roles.id", ondelete="SET NULL"),
        nullable=True
    )
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # coding, system_design, pm_case, behavioral
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # AI-generated content
    problem_statement: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    evaluation_rubric: Mapped[Optional[dict]] = mapped_column(JSON, default=list)
    red_flags: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    good_answer_outline: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Questions
    questions: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    
    # Duration
    estimated_duration_minutes: Mapped[int] = mapped_column(Integer, default=60)
    
    # Version control
    version: Mapped[int] = mapped_column(Integer, default=1)
    is_template: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="interview_kits")
    role: Mapped[Optional["Role"]] = relationship("Role", back_populates="interview_kits")
    assignments: Mapped[List["InterviewAssignment"]] = relationship(
        "InterviewAssignment",
        back_populates="interview_kit"
    )
    
    def __repr__(self) -> str:
        return f"<InterviewKit(id={self.id}, title={self.title}, type={self.type})>"


class Workflow(Base):
    """
    Workflow model for candidate pipeline management.
    """
    __tablename__ = "workflows"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False
    )
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    stages: Mapped[list] = mapped_column(JSON, default=list)  # Ordered list of stages
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="workflows")
    candidates: Mapped[List["Candidate"]] = relationship(
        "Candidate",
        back_populates="workflow"
    )
    
    def __repr__(self) -> str:
        return f"<Workflow(id={self.id}, name={self.name})>"


class InterviewAssignment(Base):
    """
    Interview assignment model - links interviewers to candidates for specific interview kits.
    """
    __tablename__ = "interview_assignments"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    candidate_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("candidates.id", ondelete="CASCADE"),
        nullable=False
    )
    interviewer_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    interview_kit_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("interview_kits.id", ondelete="SET NULL"),
        nullable=True
    )
    
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=60)
    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending, scheduled, completed, cancelled
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    feedback_required: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )
    
    # Relationships
    candidate: Mapped["Candidate"] = relationship("Candidate", back_populates="interview_assignments")
    interviewer: Mapped["User"] = relationship("User", back_populates="interview_assignments")
    interview_kit: Mapped[Optional["InterviewKit"]] = relationship("InterviewKit", back_populates="assignments")
    feedback: Mapped[Optional["Feedback"]] = relationship(
        "Feedback",
        back_populates="assignment",
        uselist=False
    )
    
    def __repr__(self) -> str:
        return f"<InterviewAssignment(id={self.id}, candidate_id={self.candidate_id}, interviewer_id={self.interviewer_id})>"


class Feedback(Base):
    """
    Feedback model - structured evaluation from interviewers.
    """
    __tablename__ = "feedbacks"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    candidate_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("candidates.id", ondelete="CASCADE"),
        nullable=False
    )
    interviewer_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    assignment_id: Mapped[Optional[str]] = mapped_column(
        String(36), 
        ForeignKey("interview_assignments.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # Competency scores (1-5 scale)
    scores: Mapped[dict] = mapped_column(JSON, default=dict)  # {competency_name: score}
    confidence: Mapped[int] = mapped_column(Integer, default=3)  # 1-5 confidence level
    
    # Written feedback
    strengths: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    weaknesses: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    recommendation: Mapped[str] = mapped_column(String(50), default="neutral")  # hire, no_hire, strong_hire, strong_no_hire, neutral
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    evidence: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)  # {competency: [evidence_text]}
    
    # AI suggestions (for improving feedback clarity)
    ai_suggestions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Status
    is_draft: Mapped[bool] = mapped_column(Boolean, default=True)
    is_submitted: Mapped[bool] = mapped_column(Boolean, default=False)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )
    
    # Relationships
    candidate: Mapped["Candidate"] = relationship("Candidate", back_populates="feedbacks")
    interviewer: Mapped["User"] = relationship("User", back_populates="feedbacks")
    assignment: Mapped[Optional["InterviewAssignment"]] = relationship("InterviewAssignment", back_populates="feedback")
    
    def __repr__(self) -> str:
        return f"<Feedback(id={self.id}, candidate_id={self.candidate_id}, recommendation={self.recommendation})>"


class StageHistory(Base):
    """
    Stage history model - tracks candidate progression through workflow stages.
    """
    __tablename__ = "stage_history"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    candidate_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("candidates.id", ondelete="CASCADE"),
        nullable=False
    )
    
    from_stage: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    to_stage: Mapped[str] = mapped_column(String(100), nullable=False)
    changed_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    candidate: Mapped["Candidate"] = relationship("Candidate", back_populates="stage_history")
    
    def __repr__(self) -> str:
        return f"<StageHistory(id={self.id}, candidate_id={self.candidate_id}, to_stage={self.to_stage})>"


class AuditLog(Base):
    """
    Audit log model for tracking important actions.
    """
    __tablename__ = "audit_logs"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[Optional[str]] = mapped_column(
        String(36), 
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    
    action: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., "user.login", "candidate.created"
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., "user", "candidate", "role"
    entity_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    old_values: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    new_values: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    audit_metadata: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="audit_logs")
    
    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action={self.action}, entity_type={self.entity_type})>"
