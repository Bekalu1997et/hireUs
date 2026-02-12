"""
End-to-end integration test for the complete interview flow.
"""
import json
import pytest
from unittest.mock import AsyncMock, patch

from app.modules.auth.service import AuthService
from app.modules.organization.service import OrganizationService
from app.modules.roles.service import RolesService
from app.modules.interview_kits.service import InterviewKitsService
from app.modules.workflows.service import WorkflowService
from app.modules.evaluations.service import EvaluationsService
from app.modules.decisions.service import DecisionsService
from app.schemas.auth import UserRegister
from app.schemas.organization import InviteRequest, InviteAccept
from app.schemas.role import RoleCreate, CompetencyCreate
from app.schemas.interview_kit import InterviewKitGenerateRequest
from app.schemas.workflow import WorkflowCreate, WorkflowStageCreate
from app.schemas.evaluation import EvaluationCreate, EvaluationScoreCreate
from app.schemas.decision import DecisionCreate


@pytest.mark.asyncio
async def test_end_to_end_interview_flow(db_session):
    """
    End-to-end flow:
    - Create org + founder
    - Invite interviewers
    - Create role + competencies
    - Generate interview kit
    - Create workflow with stages
    - Submit evaluations
    - Generate decision brief
    - Record final decision
    - Verify workflow completed + locked
    """
    # 1) Register founder + org
    auth_service = AuthService(db_session)
    founder_data = UserRegister(
        email="founder@example.com",
        password="StrongPass123",
        full_name="Founder User",
        organization_name="Test Org",
        organization_domain="testorg.com",
    )
    founder, _ = await auth_service.register_user(founder_data)

    # 2) Invite two interviewers
    org_service = OrganizationService(db_session)
    invite1 = await org_service.invite_user(
        InviteRequest(email="int1@example.com", full_name="Interviewer One"),
        founder,
    )
    invite2 = await org_service.invite_user(
        InviteRequest(email="int2@example.com", full_name="Interviewer Two"),
        founder,
    )

    interviewer1 = await org_service.accept_invite(
        InviteAccept(token=invite1["invitation_token"], password="StrongPass123")
    )
    interviewer2 = await org_service.accept_invite(
        InviteAccept(token=invite2["invitation_token"], password="StrongPass123")
    )

    # 3) Create role with competencies
    roles_service = RolesService(db_session)
    role = await roles_service.create_role(
        RoleCreate(
            title="Backend Engineer",
            description="Build APIs",
            seniority_level="senior",
            competencies=[
                CompetencyCreate(name="Python", description="Python skills", weight=0.5),
                CompetencyCreate(name="System Design", description="Design skills", weight=0.5),
            ],
        ),
        founder.organization_id,
    )

    # 4) Generate interview kit (mock AI)
    kit_service = InterviewKitsService(db_session)
    mock_kit = {
        "questions": [
            {
                "competency_id": role.competencies[0].id,
                "question_text": "Explain async in Python.",
                "evaluation_rubric": "1-5 rubric",
                "order": 1,
            },
            {
                "competency_id": role.competencies[1].id,
                "question_text": "Design a scalable API.",
                "evaluation_rubric": "1-5 rubric",
                "order": 2,
            },
        ]
    }
    with patch.object(
        kit_service.ai_client,
        "generate_interview_kit",
        new=AsyncMock(return_value=json.dumps(mock_kit)),
    ):
        kit = await kit_service.generate_interview_kit(
            InterviewKitGenerateRequest(role_id=role.id),
            founder,
        )
    assert kit.role_id == role.id

    # 5) Create workflow with stages
    workflow_service = WorkflowService(db_session)
    workflow = await workflow_service.create_workflow(
        WorkflowCreate(
            candidate={"full_name": "Candidate A", "email": "cand@example.com"},
            role_id=role.id,
            stages=[
                WorkflowStageCreate(interviewer_id=interviewer1.id, stage_order=1),
                WorkflowStageCreate(interviewer_id=interviewer2.id, stage_order=2),
            ],
        ),
        founder,
    )
    assert workflow.status == "pending"
    assert len(workflow.stages) == 2

    # Map stage order to stage
    stage_by_order = {s.stage_order: s for s in workflow.stages}

    # 6) Submit evaluations (two stages)
    eval_service = EvaluationsService(db_session)
    await eval_service.submit_evaluation(
        EvaluationCreate(
            workflow_id=workflow.id,
            workflow_stage_id=stage_by_order[1].id,
            notes="Good Python skills",
            scores=[
                EvaluationScoreCreate(competency_id=role.competencies[0].id, score=4),
                EvaluationScoreCreate(competency_id=role.competencies[1].id, score=3),
            ],
        ),
        interviewer1,
    )
    await eval_service.submit_evaluation(
        EvaluationCreate(
            workflow_id=workflow.id,
            workflow_stage_id=stage_by_order[2].id,
            notes="Strong design",
            scores=[
                EvaluationScoreCreate(competency_id=role.competencies[0].id, score=4),
                EvaluationScoreCreate(competency_id=role.competencies[1].id, score=5),
            ],
        ),
        interviewer2,
    )

    # 7) Generate decision brief (mock AI)
    decisions_service = DecisionsService(db_session)
    mock_brief = {
        "summary": "Solid candidate",
        "strengths": "Strong design skills",
        "concerns": "None",
        "recommendation": "Recommend hiring",
    }
    with patch.object(
        decisions_service.ai_client,
        "generate_decision_brief",
        new=AsyncMock(return_value=json.dumps(mock_brief)),
    ):
        brief = await decisions_service.generate_decision_brief(workflow.id, founder)
    assert brief.summary == mock_brief["summary"]

    # 8) Record final decision
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

    # 9) Verify workflow completed + locked
    updated_workflow = await workflow_service.get_workflow(workflow.id, founder)
    assert updated_workflow.status == "completed"
    assert updated_workflow.is_locked is True
