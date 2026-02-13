"""
Property-based tests for core platform requirements.
"""
import json
import pytest
from datetime import timedelta
from unittest.mock import AsyncMock
from hypothesis import given, settings, strategies as st
from sqlalchemy.exc import IntegrityError

from app.core.security import create_access_token, decode_access_token
from app.modules.auth.service import AuthService
from app.modules.organization.service import OrganizationService
from app.modules.roles.service import RolesService
from app.modules.interview_kits.service import InterviewKitsService
from app.modules.workflows.service import WorkflowService
from app.modules.evaluations.service import EvaluationsService
from app.modules.decisions.service import DecisionsService
from app.modules.signals.service import SignalsService
from app.modules.ai.prompts import build_interview_kit_prompt, build_decision_brief_prompt
from app.schemas.auth import UserRegister
from app.schemas.organization import InviteRequest, InviteAccept
from app.schemas.role import RoleCreate, CompetencyCreate
from app.schemas.interview_kit import InterviewKitGenerateRequest
from app.schemas.workflow import WorkflowCreate, WorkflowStageCreate, WorkflowStagesUpdate, WorkflowStageUpdate
from app.schemas.evaluation import EvaluationCreate, EvaluationScoreCreate
from app.schemas.decision import DecisionCreate
from app.db.models import Evaluation


@pytest.mark.asyncio
@settings(max_examples=5)
@given(
    org_name=st.text(min_size=1, max_size=50),
    suffix=st.uuids(),
)
async def test_property_org_creation_completeness(db_session, org_name, suffix):
    """
    Property 1: Organization Creation Completeness
    """
    service = AuthService(db_session)
    email = f"user{suffix.hex}@example.com"
    org_domain = f"org{suffix.hex}"
    user, _ = await service.register_user(
        UserRegister(
            email=email,
            password="StrongPass123",
            full_name="Founder",
            organization_name=org_name,
            organization_domain=org_domain,
        )
    )
    assert user.organization.name == org_name
    assert user.organization.domain == org_domain
    assert user.role == "founder"


@pytest.mark.asyncio
async def test_property_invitation_round_trip(db_session):
    """
    Property 3: Invitation Round Trip
    """
    auth_service = AuthService(db_session)
    founder, _ = await auth_service.register_user(
        UserRegister(
            email="founder@org.com",
            password="StrongPass123",
            full_name="Founder",
            organization_name="Org",
            organization_domain="orgdomain",
        )
    )
    org_service = OrganizationService(db_session)
    invite = await org_service.invite_user(
        InviteRequest(email="int@org.com", full_name="Interviewer"),
        founder,
    )
    interviewer = await org_service.accept_invite(
        InviteAccept(token=invite["invitation_token"], password="StrongPass123")
    )
    assert interviewer.organization_id == founder.organization_id
    assert interviewer.role == "interviewer"


@pytest.mark.asyncio
@settings(max_examples=5)
@given(
    title=st.text(min_size=1, max_size=30),
    desc=st.text(min_size=5, max_size=100),
    suffix=st.uuids(),
)
async def test_property_interview_kit_generation_and_storage(db_session, title, desc, suffix):
    """
    Property 12 + 13: LLM Interview Kit Generation and Storage
    """
    auth_service = AuthService(db_session)
    founder, _ = await auth_service.register_user(
        UserRegister(
            email=f"{suffix.hex}@example.com",
            password="StrongPass123",
            full_name="Founder",
            organization_name="Org",
            organization_domain=f"org{suffix.hex}",
        )
    )
    roles_service = RolesService(db_session)
    role = await roles_service.create_role(
        RoleCreate(
            title=title,
            description=desc,
            seniority_level="senior",
            competencies=[
                CompetencyCreate(name="Python", description="Python", weight=0.5),
                CompetencyCreate(name="Design", description="Design", weight=0.5),
            ],
        ),
        founder.organization_id,
    )
    kit_service = InterviewKitsService(db_session)
    mock_kit = {
        "questions": [
            {
                "competency_id": role.competencies[0].id,
                "question_text": "Q1",
                "evaluation_rubric": "R1",
                "order": 1,
            },
            {
                "competency_id": role.competencies[1].id,
                "question_text": "Q2",
                "evaluation_rubric": "R2",
                "order": 2,
            },
        ]
    }
    kit_service.ai_client.generate_interview_kit = AsyncMock(
        return_value=json.dumps(mock_kit)
    )
    kit = await kit_service.generate_interview_kit(
        InterviewKitGenerateRequest(role_id=role.id),
        founder,
    )
    assert kit.role_id == role.id
    assert len(kit.questions) == 2


@pytest.mark.asyncio
async def test_property_workflow_creation_and_stage_assignment(db_session):
    """
    Property 14 + 15 + 2: Workflow creation completeness, stage assignment, IDs.
    """
    auth_service = AuthService(db_session)
    founder, _ = await auth_service.register_user(
        UserRegister(
            email="founder2@org.com",
            password="StrongPass123",
            full_name="Founder",
            organization_name="Org2",
            organization_domain="org2",
        )
    )
    org_service = OrganizationService(db_session)
    invite = await org_service.invite_user(
        InviteRequest(email="int2@org.com", full_name="Interviewer"),
        founder,
    )
    interviewer = await org_service.accept_invite(
        InviteAccept(token=invite["invitation_token"], password="StrongPass123")
    )
    roles_service = RolesService(db_session)
    role = await roles_service.create_role(
        RoleCreate(
            title="Role",
            description="Desc",
            seniority_level="senior",
            competencies=[CompetencyCreate(name="A", description="A", weight=1.0)],
        ),
        founder.organization_id,
    )
    workflow_service = WorkflowService(db_session)
    workflow = await workflow_service.create_workflow(
        WorkflowCreate(
            candidate={"full_name": "C", "email": "c@x.com"},
            role_id=role.id,
            stages=[WorkflowStageCreate(interviewer_id=interviewer.id, stage_order=1)],
        ),
        founder,
    )
    assert workflow.id is not None
    assert workflow.status == "pending"
    assert workflow.stages[0].id is not None
    assert workflow.stages[0].interviewer_id == interviewer.id


@pytest.mark.asyncio
async def test_property_evaluation_validation_and_state_transition(db_session):
    """
    Property 16 + 17: Evaluation validation + stage transition.
    """
    auth_service = AuthService(db_session)
    founder, _ = await auth_service.register_user(
        UserRegister(
            email="founder3@org.com",
            password="StrongPass123",
            full_name="Founder",
            organization_name="Org3",
            organization_domain="org3",
        )
    )
    org_service = OrganizationService(db_session)
    invite = await org_service.invite_user(
        InviteRequest(email="int3@org.com", full_name="Interviewer"),
        founder,
    )
    interviewer = await org_service.accept_invite(
        InviteAccept(token=invite["invitation_token"], password="StrongPass123")
    )
    roles_service = RolesService(db_session)
    role = await roles_service.create_role(
        RoleCreate(
            title="Role",
            description="Desc",
            seniority_level="senior",
            competencies=[CompetencyCreate(name="A", description="A", weight=1.0)],
        ),
        founder.organization_id,
    )
    workflow_service = WorkflowService(db_session)
    workflow = await workflow_service.create_workflow(
        WorkflowCreate(
            candidate={"full_name": "C", "email": "c2@x.com"},
            role_id=role.id,
            stages=[WorkflowStageCreate(interviewer_id=interviewer.id, stage_order=1)],
        ),
        founder,
    )
    stage = workflow.stages[0]
    eval_service = EvaluationsService(db_session)
    evaluation = await eval_service.submit_evaluation(
        EvaluationCreate(
            workflow_id=workflow.id,
            workflow_stage_id=stage.id,
            notes="OK",
            scores=[EvaluationScoreCreate(competency_id=role.competencies[0].id, score=4)],
        ),
        interviewer,
    )
    assert evaluation.id is not None
    updated_workflow = await workflow_service.get_workflow(workflow.id, founder)
    assert updated_workflow.stages[0].status == "completed"


@pytest.mark.asyncio
async def test_property_signals_aggregation(db_session):
    """
    Property 18 + 19: Signals completeness + score calculation.
    """
    auth_service = AuthService(db_session)
    founder, _ = await auth_service.register_user(
        UserRegister(
            email="founder4@org.com",
            password="StrongPass123",
            full_name="Founder",
            organization_name="Org4",
            organization_domain="org4",
        )
    )
    org_service = OrganizationService(db_session)
    invite = await org_service.invite_user(
        InviteRequest(email="int4@org.com", full_name="Interviewer"),
        founder,
    )
    interviewer = await org_service.accept_invite(
        InviteAccept(token=invite["invitation_token"], password="StrongPass123")
    )
    roles_service = RolesService(db_session)
    role = await roles_service.create_role(
        RoleCreate(
            title="Role",
            description="Desc",
            seniority_level="senior",
            competencies=[
                CompetencyCreate(name="A", description="A", weight=0.5),
                CompetencyCreate(name="B", description="B", weight=0.5),
            ],
        ),
        founder.organization_id,
    )
    workflow_service = WorkflowService(db_session)
    workflow = await workflow_service.create_workflow(
        WorkflowCreate(
            candidate={"full_name": "C", "email": "c3@x.com"},
            role_id=role.id,
            stages=[WorkflowStageCreate(interviewer_id=interviewer.id, stage_order=1)],
        ),
        founder,
    )
    eval_service = EvaluationsService(db_session)
    await eval_service.submit_evaluation(
        EvaluationCreate(
            workflow_id=workflow.id,
            workflow_stage_id=workflow.stages[0].id,
            notes="OK",
            scores=[
                EvaluationScoreCreate(competency_id=role.competencies[0].id, score=4),
                EvaluationScoreCreate(competency_id=role.competencies[1].id, score=2),
            ],
        ),
        interviewer,
    )
    signals = await SignalsService(db_session).get_signals(
        candidate_id=workflow.candidate_id,
        role_id=role.id,
        user=founder,
    )
    assert signals.candidate_id == workflow.candidate_id
    assert signals.role_id == role.id
    assert signals.overall_weighted_score is not None


@pytest.mark.asyncio
async def test_property_decision_recording_and_immutability(db_session):
    """
    Property 20-23: Decision brief generation + record + immutability.
    """
    auth_service = AuthService(db_session)
    founder, _ = await auth_service.register_user(
        UserRegister(
            email="founder5@org.com",
            password="StrongPass123",
            full_name="Founder",
            organization_name="Org5",
            organization_domain="org5",
        )
    )
    org_service = OrganizationService(db_session)
    invite = await org_service.invite_user(
        InviteRequest(email="int5@org.com", full_name="Interviewer"),
        founder,
    )
    interviewer = await org_service.accept_invite(
        InviteAccept(token=invite["invitation_token"], password="StrongPass123")
    )
    roles_service = RolesService(db_session)
    role = await roles_service.create_role(
        RoleCreate(
            title="Role",
            description="Desc",
            seniority_level="senior",
            competencies=[CompetencyCreate(name="A", description="A", weight=1.0)],
        ),
        founder.organization_id,
    )
    workflow_service = WorkflowService(db_session)
    workflow = await workflow_service.create_workflow(
        WorkflowCreate(
            candidate={"full_name": "C", "email": "c4@x.com"},
            role_id=role.id,
            stages=[WorkflowStageCreate(interviewer_id=interviewer.id, stage_order=1)],
        ),
        founder,
    )
    await EvaluationsService(db_session).submit_evaluation(
        EvaluationCreate(
            workflow_id=workflow.id,
            workflow_stage_id=workflow.stages[0].id,
            notes="OK",
            scores=[EvaluationScoreCreate(competency_id=role.competencies[0].id, score=4)],
        ),
        interviewer,
    )
    decisions_service = DecisionsService(db_session)
    decisions_service.ai_client.generate_decision_brief = AsyncMock(
        return_value=json.dumps(
            {
                "summary": "Good",
                "strengths": "A",
                "concerns": "None",
                "recommendation": "Recommend hiring",
            }
        )
    )
    brief = await decisions_service.generate_decision_brief(workflow.id, founder)
    decision = await decisions_service.record_decision(
        DecisionCreate(
            workflow_id=workflow.id,
            outcome="hire",
            summary=brief.summary,
            strengths=brief.strengths,
            concerns=brief.concerns,
            recommendation=brief.recommendation,
        ),
        founder,
    )
    assert decision.workflow_id == workflow.id
    with pytest.raises(Exception):
        await workflow_service.update_workflow_stages(
            workflow.id,
            WorkflowStagesUpdate(
                stages=[WorkflowStageUpdate(id=workflow.stages[0].id, interviewer_id=interviewer.id)]
            ),
            founder,
        )


def test_property_token_expiration_enforcement():
    """
    Property 6: Token Expiration Enforcement
    """
    token = create_access_token({"sub": "x"}, expires_delta=timedelta(seconds=-1))
    assert decode_access_token(token) is None


def test_property_prompt_context_inclusion():
    """
    Property 27: Prompt Context Inclusion
    """
    prompt = build_interview_kit_prompt(
        role_title="Role",
        role_description="Desc",
        seniority_level="senior",
        competencies=[{"id": 1, "name": "A", "description": "D", "weight": 1.0}],
    )
    assert "Role" in prompt and "Desc" in prompt

    prompt2 = build_decision_brief_prompt(
        candidate_name="Cand",
        role_title="Role",
        role_description="Desc",
        competencies=[{"name": "A", "description": "D", "weight": 1.0}],
        evaluations=[],
        aggregated_scores={"A": 4.5},
    )
    assert "Cand" in prompt2 and "A" in prompt2


@pytest.mark.asyncio
async def test_property_referential_integrity_enforcement(db_session):
    """
    Property 24: Referential Integrity Enforcement
    """
    # Try to insert evaluation score with invalid competency_id
    db_session.add(
        Evaluation(
            workflow_id=9999,
            workflow_stage_id=9999,
            interviewer_id=9999,
            notes="x",
        )
    )
    with pytest.raises(IntegrityError):
        await db_session.flush()
    await db_session.rollback()


def test_property_input_validation_before_persistence():
    """
    Property 25: Input Validation Before Persistence
    """
    with pytest.raises(Exception):
        RoleCreate(
            title="",
            description="Desc",
            seniority_level="senior",
            competencies=[CompetencyCreate(name="A", description="A", weight=1.0)],
        )
