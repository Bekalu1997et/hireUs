"""initial schema

Revision ID: 20260212_2359
Revises: 
Create Date: 2026-02-12 23:59:00
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260212_2359"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "organizations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("domain", sa.String(length=255), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("organization_id", sa.Integer(), sa.ForeignKey("organizations.id")),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("seniority_level", sa.String(length=50), nullable=False),
        sa.Column("organization_id", sa.Integer(), sa.ForeignKey("organizations.id")),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "competencies",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False),
        sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.id")),
    )

    op.create_table(
        "interview_kits",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.id")),
        sa.Column("generated_at", sa.DateTime(), nullable=False),
        sa.Column("llm_model", sa.String(length=100), nullable=False),
    )

    op.create_table(
        "interview_questions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("interview_kit_id", sa.Integer(), sa.ForeignKey("interview_kits.id")),
        sa.Column("competency_id", sa.Integer(), sa.ForeignKey("competencies.id")),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("evaluation_rubric", sa.Text(), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False),
    )

    op.create_table(
        "candidates",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "workflows",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("candidate_id", sa.Integer(), sa.ForeignKey("candidates.id")),
        sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.id")),
        sa.Column("organization_id", sa.Integer(), sa.ForeignKey("organizations.id")),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("is_locked", sa.Boolean(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("reopened_at", sa.DateTime(), nullable=True),
        sa.Column("reopen_reason", sa.Text(), nullable=True),
    )

    op.create_table(
        "workflow_stages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("workflow_id", sa.Integer(), sa.ForeignKey("workflows.id")),
        sa.Column("interviewer_id", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("stage_order", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.CheckConstraint("stage_order >= 1", name="ck_workflow_stage_order_positive"),
        sa.UniqueConstraint("workflow_id", "stage_order", name="uq_workflow_stage_order"),
    )

    op.create_table(
        "evaluations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("workflow_id", sa.Integer(), sa.ForeignKey("workflows.id")),
        sa.Column("workflow_stage_id", sa.Integer(), sa.ForeignKey("workflow_stages.id")),
        sa.Column("interviewer_id", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("notes", sa.Text(), nullable=False),
        sa.Column("submitted_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "evaluation_scores",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("evaluation_id", sa.Integer(), sa.ForeignKey("evaluations.id")),
        sa.Column("competency_id", sa.Integer(), sa.ForeignKey("competencies.id")),
        sa.Column("score", sa.Integer(), nullable=False),
    )

    op.create_table(
        "decisions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("workflow_id", sa.Integer(), sa.ForeignKey("workflows.id")),
        sa.Column("candidate_id", sa.Integer(), sa.ForeignKey("candidates.id")),
        sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.id")),
        sa.Column("decision_maker_id", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("outcome", sa.String(length=50), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("strengths", sa.Text(), nullable=False),
        sa.Column("concerns", sa.Text(), nullable=False),
        sa.Column("recommendation", sa.Text(), nullable=False),
        sa.Column("decided_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "role_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("workflow_id", sa.Integer(), sa.ForeignKey("workflows.id"), unique=True),
        sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.id")),
        sa.Column("data", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("entity_type", sa.String(length=50), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("actor_id", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("before_data", sa.JSON(), nullable=True),
        sa.Column("after_data", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )


def downgrade():
    op.drop_table("audit_logs")
    op.drop_table("role_snapshots")
    op.drop_table("decisions")
    op.drop_table("evaluation_scores")
    op.drop_table("evaluations")
    op.drop_table("workflow_stages")
    op.drop_table("workflows")
    op.drop_table("candidates")
    op.drop_table("interview_questions")
    op.drop_table("interview_kits")
    op.drop_table("competencies")
    op.drop_table("roles")
    op.drop_table("users")
    op.drop_table("organizations")
