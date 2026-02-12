"""
Database models for the Structured Interview Platform.

All models use SQLAlchemy 2.0 with async support and type annotations.
"""
from datetime import datetime
from typing import List, Optional

from sqlalchemy import String, Text, Integer, Float, ForeignKey, UniqueConstraint, CheckConstraint, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Organization(Base):
    """
    Organization model representing a company using the platform.
    
    An organization has multiple users, roles, and workflows.
    """
    __tablename__ = "organizations"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    domain: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    # Relationships
    users: Mapped[List["User"]] = relationship(back_populates="organization", cascade="all, delete-orphan")
    roles: Mapped[List["Role"]] = relationship(back_populates="organization", cascade="all, delete-orphan")
    workflows: Mapped[List["Workflow"]] = relationship(back_populates="organization", cascade="all, delete-orphan")


class User(Base):
    """
    User model representing a platform user (founder or interviewer).
    
    Users belong to an organization and can submit evaluations.
    Passwords are stored as bcrypt hashes.
    """
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)  # "founder" or "interviewer"
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    # Relationships
    organization: Mapped["Organization"] = relationship(back_populates="users")
    evaluations: Mapped[List["Evaluation"]] = relationship(back_populates="interviewer")


class Role(Base):
    """
    Role model representing a job position with competencies.
    
    Roles define what competencies are required and drive interview kit generation.
    """
    __tablename__ = "roles"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    seniority_level: Mapped[str] = mapped_column(String(50), nullable=False)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    # Relationships
    organization: Mapped["Organization"] = relationship(back_populates="roles")
    competencies: Mapped[List["Competency"]] = relationship(back_populates="role", cascade="all, delete-orphan")
    interview_kits: Mapped[List["InterviewKit"]] = relationship(back_populates="role")
    workflows: Mapped[List["Workflow"]] = relationship(back_populates="role")


class Competency(Base):
    """
    Competency model representing a skill required for a role.
    
    Competencies have weights that sum to 1.0 for scoring calculations.
    """
    __tablename__ = "competencies"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))
    
    # Relationships
    role: Mapped["Role"] = relationship(back_populates="competencies")
    evaluation_scores: Mapped[List["EvaluationScore"]] = relationship(back_populates="competency")


class InterviewKit(Base):
    """
    InterviewKit model representing an AI-generated set of interview questions.
    
    Interview kits are generated for specific roles and contain questions
    mapped to competencies.
    """
    __tablename__ = "interview_kits"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))
    generated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    llm_model: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Relationships
    role: Mapped["Role"] = relationship(back_populates="interview_kits")
    questions: Mapped[List["InterviewQuestion"]] = relationship(back_populates="interview_kit", cascade="all, delete-orphan")


class InterviewQuestion(Base):
    """
    InterviewQuestion model representing a single interview question.
    
    Questions are part of an interview kit and map to specific competencies.
    """
    __tablename__ = "interview_questions"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    interview_kit_id: Mapped[int] = mapped_column(ForeignKey("interview_kits.id"))
    competency_id: Mapped[int] = mapped_column(ForeignKey("competencies.id"))
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    evaluation_rubric: Mapped[str] = mapped_column(Text, nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Relationships
    interview_kit: Mapped["InterviewKit"] = relationship(back_populates="questions")
    competency: Mapped["Competency"] = relationship()


class Candidate(Base):
    """
    Candidate model representing a job applicant.
    
    Candidates are evaluated through workflows.
    """
    __tablename__ = "candidates"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    # Relationships
    workflows: Mapped[List["Workflow"]] = relationship(back_populates="candidate")


class Workflow(Base):
    """
    Workflow model representing the interview process for a candidate-role pairing.
    
    Workflows orchestrate the interview stages and track overall status.
    """
    __tablename__ = "workflows"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"))
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    is_locked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reopened_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    reopen_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    candidate: Mapped["Candidate"] = relationship(back_populates="workflows")
    role: Mapped["Role"] = relationship(back_populates="workflows")
    organization: Mapped["Organization"] = relationship(back_populates="workflows")
    stages: Mapped[List["WorkflowStage"]] = relationship(back_populates="workflow", cascade="all, delete-orphan")
    evaluations: Mapped[List["Evaluation"]] = relationship(back_populates="workflow")
    decision: Mapped[Optional["Decision"]] = relationship(back_populates="workflow", uselist=False)
    role_snapshot: Mapped[Optional["RoleSnapshot"]] = relationship(back_populates="workflow", uselist=False)


class RoleSnapshot(Base):
    """
    RoleSnapshot model representing a frozen role definition for a workflow.

    Captures role fields and competencies at workflow creation time.
    """
    __tablename__ = "role_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)
    workflow_id: Mapped[int] = mapped_column(ForeignKey("workflows.id"), unique=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))
    data: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    workflow: Mapped["Workflow"] = relationship(back_populates="role_snapshot")
    role: Mapped["Role"] = relationship()


class AuditLog(Base):
    """
    AuditLog model for tracking changes to critical entities.
    """
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[int] = mapped_column(Integer, nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    actor_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    before_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    after_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    actor: Mapped["User"] = relationship()


class WorkflowStage(Base):
    """
    WorkflowStage model representing a single interview stage in a workflow.
    
    Each stage is assigned to an interviewer and tracks completion status.
    """
    __tablename__ = "workflow_stages"
    __table_args__ = (
        UniqueConstraint("workflow_id", "stage_order", name="uq_workflow_stage_order"),
        CheckConstraint("stage_order >= 1", name="ck_workflow_stage_order_positive"),
    )
    
    id: Mapped[int] = mapped_column(primary_key=True)
    workflow_id: Mapped[int] = mapped_column(ForeignKey("workflows.id"))
    interviewer_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    stage_order: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    
    # Relationships
    workflow: Mapped["Workflow"] = relationship(back_populates="stages")
    interviewer: Mapped["User"] = relationship()


class Evaluation(Base):
    """
    Evaluation model representing an interviewer's assessment of a candidate.
    
    Evaluations contain competency scores and notes.
    """
    __tablename__ = "evaluations"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    workflow_id: Mapped[int] = mapped_column(ForeignKey("workflows.id"))
    workflow_stage_id: Mapped[int] = mapped_column(ForeignKey("workflow_stages.id"))
    interviewer_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    notes: Mapped[str] = mapped_column(Text, nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    # Relationships
    workflow: Mapped["Workflow"] = relationship(back_populates="evaluations")
    workflow_stage: Mapped["WorkflowStage"] = relationship()
    interviewer: Mapped["User"] = relationship(back_populates="evaluations")
    scores: Mapped[List["EvaluationScore"]] = relationship(back_populates="evaluation", cascade="all, delete-orphan")


class EvaluationScore(Base):
    """
    EvaluationScore model representing a score for a specific competency.
    
    Scores are integers from 1-5.
    """
    __tablename__ = "evaluation_scores"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    evaluation_id: Mapped[int] = mapped_column(ForeignKey("evaluations.id"))
    competency_id: Mapped[int] = mapped_column(ForeignKey("competencies.id"))
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Relationships
    evaluation: Mapped["Evaluation"] = relationship(back_populates="scores")
    competency: Mapped["Competency"] = relationship(back_populates="evaluation_scores")


class Decision(Base):
    """
    Decision model representing the final hiring decision for a workflow.
    
    Decisions include AI-generated briefs and final outcomes.
    """
    __tablename__ = "decisions"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    workflow_id: Mapped[int] = mapped_column(ForeignKey("workflows.id"))
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"))
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))
    decision_maker_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    outcome: Mapped[str] = mapped_column(String(50), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    strengths: Mapped[str] = mapped_column(Text, nullable=False)
    concerns: Mapped[str] = mapped_column(Text, nullable=False)
    recommendation: Mapped[str] = mapped_column(Text, nullable=False)
    decided_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    # Relationships
    workflow: Mapped["Workflow"] = relationship(back_populates="decision")
    decision_maker: Mapped["User"] = relationship()
    candidate: Mapped["Candidate"] = relationship()
    role: Mapped["Role"] = relationship()
