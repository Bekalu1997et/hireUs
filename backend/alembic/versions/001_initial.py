"""Initial migration - create all tables

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types
    user_role_enum = postgresql.ENUM(
        'superadmin', 'admin', 'recruiter', 'interviewer', 'hiring_manager', 'candidate',
        name='userrole', create_type=False
    )
    org_member_role_enum = postgresql.ENUM(
        'owner', 'admin', 'member', 'viewer',
        name='organizationmemberrole', create_type=False
    )
    
    user_role_enum.create(op.get_bind(), checkfirst=True)
    org_member_role_enum.create(op.get_bind(), checkfirst=True)
    
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=True),
        sa.Column('phone', sa.String(50), nullable=True),
        sa.Column('avatar_url', sa.String(500), nullable=True),
        sa.Column('role', user_role_enum, nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_superuser', sa.Boolean(), default=False),
        sa.Column('email_verified', sa.Boolean(), default=False),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_users_email', 'users', ['email'])
    
    # Organizations table
    op.create_table(
        'organizations',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False, unique=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('logo_url', sa.String(500), nullable=True),
        sa.Column('website', sa.String(255), nullable=True),
        sa.Column('industry', sa.String(100), nullable=True),
        sa.Column('size', sa.String(50), nullable=True),
        sa.Column('settings', postgresql.JSON(astext_type=sa.Text()), default={}),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_organizations_slug', 'organizations', ['slug'])
    
    # Organization members table
    op.create_table(
        'organization_members',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('organization_id', sa.String(36), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', org_member_role_enum, nullable=False),
        sa.Column('invited_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('accepted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('invited_by', sa.String(36), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
    )
    op.create_index('ix_organization_members_user_org', 'organization_members', ['user_id', 'organization_id'], unique=True)
    
    # Roles table
    op.create_table(
        'roles',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('organization_id', sa.String(36), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('seniority', sa.String(50), nullable=True),
        sa.Column('department', sa.String(100), nullable=True),
        sa.Column('tech_stack', postgresql.JSON(astext_type=sa.Text()), default=[]),
        sa.Column('core_competencies', postgresql.JSON(astext_type=sa.Text()), default=[]),
        sa.Column('interview_stages', postgresql.JSON(astext_type=sa.Text()), default=[]),
        sa.Column('mission', sa.Text(), nullable=True),
        sa.Column('must_have', postgresql.JSON(astext_type=sa.Text()), default=[]),
        sa.Column('nice_to_have', postgresql.JSON(astext_type=sa.Text()), default=[]),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_by', sa.String(36), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_roles_slug', 'roles', ['slug'])
    
    # Workflows table
    op.create_table(
        'workflows',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('organization_id', sa.String(36), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('stages', postgresql.JSON(astext_type=sa.Text()), default=[]),
        sa.Column('is_default', sa.Boolean(), default=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_by', sa.String(36), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    
    # Interview kits table
    op.create_table(
        'interview_kits',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('organization_id', sa.String(36), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role_id', sa.String(36), sa.ForeignKey('roles.id', ondelete='SET NULL'), nullable=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('problem_statement', sa.Text(), nullable=True),
        sa.Column('evaluation_rubric', postgresql.JSON(astext_type=sa.Text()), default=[]),
        sa.Column('red_flags', postgresql.JSON(astext_type=sa.Text()), default=[]),
        sa.Column('good_answer_outline', sa.Text(), nullable=True),
        sa.Column('questions', postgresql.JSON(astext_type=sa.Text()), default=[]),
        sa.Column('estimated_duration_minutes', sa.Integer(), default=60),
        sa.Column('version', sa.Integer(), default=1),
        sa.Column('is_template', sa.Boolean(), default=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_by', sa.String(36), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    
    # Candidates table
    op.create_table(
        'candidates',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('organization_id', sa.String(36), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role_id', sa.String(36), sa.ForeignKey('roles.id', ondelete='SET NULL'), nullable=True),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('phone', sa.String(50), nullable=True),
        sa.Column('linkedin_url', sa.String(500), nullable=True),
        sa.Column('resume_url', sa.String(500), nullable=True),
        sa.Column('portfolio_url', sa.String(500), nullable=True),
        sa.Column('ai_summary', sa.Text(), nullable=True),
        sa.Column('workflow_id', sa.String(36), sa.ForeignKey('workflows.id'), nullable=True),
        sa.Column('current_stage_id', sa.String(36), nullable=True),
        sa.Column('status', sa.String(50), default='applied'),
        sa.Column('source', sa.String(100), nullable=True),
        sa.Column('candidate_metadata', postgresql.JSON(astext_type=sa.Text()), default={}),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_by', sa.String(36), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_candidates_email', 'candidates', ['email'])
    
    # Interview assignments table
    op.create_table(
        'interview_assignments',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('candidate_id', sa.String(36), sa.ForeignKey('candidates.id', ondelete='CASCADE'), nullable=False),
        sa.Column('interviewer_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('interview_kit_id', sa.String(36), sa.ForeignKey('interview_kits.id', ondelete='SET NULL'), nullable=True),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_minutes', sa.Integer(), default=60),
        sa.Column('status', sa.String(50), default='pending'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('feedback_required', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    
    # Feedbacks table
    op.create_table(
        'feedbacks',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('candidate_id', sa.String(36), sa.ForeignKey('candidates.id', ondelete='CASCADE'), nullable=False),
        sa.Column('interviewer_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('assignment_id', sa.String(36), sa.ForeignKey('interview_assignments.id', ondelete='SET NULL'), nullable=True),
        sa.Column('scores', postgresql.JSON(astext_type=sa.Text()), default={}),
        sa.Column('confidence', sa.Integer(), default=3),
        sa.Column('strengths', sa.Text(), nullable=True),
        sa.Column('weaknesses', sa.Text(), nullable=True),
        sa.Column('recommendation', sa.String(50), default='neutral'),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('evidence', postgresql.JSON(astext_type=sa.Text()), default={}),
        sa.Column('ai_suggestions', sa.Text(), nullable=True),
        sa.Column('is_draft', sa.Boolean(), default=True),
        sa.Column('is_submitted', sa.Boolean(), default=False),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    
    # Stage history table
    op.create_table(
        'stage_history',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('candidate_id', sa.String(36), sa.ForeignKey('candidates.id', ondelete='CASCADE'), nullable=False),
        sa.Column('from_stage', sa.String(100), nullable=True),
        sa.Column('to_stage', sa.String(100), nullable=False),
        sa.Column('changed_by', sa.String(36), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    
    # Audit logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('entity_type', sa.String(100), nullable=False),
        sa.Column('entity_id', sa.String(36), nullable=True),
        sa.Column('old_values', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('new_values', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('audit_metadata', postgresql.JSON(astext_type=sa.Text()), default={}),
        sa.Column('ip_address', sa.String(50), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('stage_history')
    op.drop_table('feedbacks')
    op.drop_table('interview_assignments')
    op.drop_table('candidates')
    op.drop_table('interview_kits')
    op.drop_table('workflows')
    op.drop_table('roles')
    op.drop_table('organization_members')
    op.drop_table('organizations')
    op.drop_table('users')
    
    # Drop enum types
    op.execute('DROP TYPE IF EXISTS userrole')
    op.execute('DROP TYPE IF EXISTS organizationmemberrole')

