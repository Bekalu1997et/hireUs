"""
Unit tests for Workflows module.
Tests workflow schemas, validation, and transitions.
"""
import pytest
from datetime import datetime
from app.schemas.workflow import (
    WorkflowStage,
    WorkflowStageCreate,
    WorkflowStageUpdate,
    WorkflowBase,
    WorkflowCreate,
    WorkflowUpdate,
    WorkflowResponse,
    WorkflowListResponse,
    WorkflowDetailResponse,
    CandidateStageInfo,
    MoveCandidateRequest,
    BulkMoveCandidateRequest,
    StageTransitionResult,
    BulkStageTransitionResult,
    InterviewerAssignmentRequest,
    InterviewerReassignmentRequest,
    CancelAssignmentRequest,
    AssignmentResponse,
    StageAssignmentsResponse,
    FeedbackStatusResponse,
    PendingFeedbackResponse,
    FeedbackCompletionStats,
    DefaultWorkflowTemplate,
    WorkflowTemplateResponse,
    CanMoveCandidateResponse,
    WorkflowStageStats,
    WorkflowStatsResponse,
)


# ============== WorkflowStage Tests ==============

@pytest.mark.workflows
class TestWorkflowStage:
    """Tests for WorkflowStage schema."""

    def test_workflow_stage_valid(self):
        """Test valid workflow stage."""
        data = {
            "id": "stage_1",
            "name": "Application Review",
            "order": 0,
            "description": "Initial review of application",
            "color": "#6366f1",
            "required_feedback_count": 0,
            "interview_types": []
        }
        stage = WorkflowStage(**data)
        assert stage.id == "stage_1"
        assert stage.name == "Application Review"
        assert stage.order == 0

    def test_workflow_stage_default_color(self):
        """Test workflow stage with default color."""
        data = {
            "id": "stage_2",
            "name": "Phone Screen",
            "order": 1
        }
        stage = WorkflowStage(**data)
        assert stage.color == "#6366f1"
        assert stage.required_feedback_count == 0

    def test_workflow_stage_with_interview_types(self):
        """Test workflow stage with interview types."""
        data = {
            "id": "stage_3",
            "name": "Technical Interview",
            "order": 2,
            "interview_types": ["coding", "system_design"]
        }
        stage = WorkflowStage(**data)
        assert len(stage.interview_types) == 2

    def test_workflow_stage_order_negative(self):
        """Test workflow stage with negative order raises error."""
        with pytest.raises(ValueError):
            WorkflowStage(id="stage_x", name="Test", order=-1)


# ============== WorkflowStageCreate Tests ==============

@pytest.mark.workflows
class TestWorkflowStageCreate:
    """Tests for WorkflowStageCreate schema."""

    def test_stage_create_valid(self):
        """Test valid stage creation."""
        data = {
            "name": "Technical Screen",
            "description": "Technical screening",
            "required_feedback_count": 1
        }
        stage = WorkflowStageCreate(**data)
        assert stage.name == "Technical Screen"
        assert stage.required_feedback_count == 1

    def test_stage_create_minimal(self):
        """Test minimal stage creation."""
        data = {"name": "Basic Stage"}
        stage = WorkflowStageCreate(**data)
        assert stage.name == "Basic Stage"
        assert stage.interview_types == []

    def test_stage_create_name_too_long(self):
        """Test stage creation with name exceeding max length."""
        with pytest.raises(ValueError):
            WorkflowStageCreate(name="a" * 101)


# ============== WorkflowStageUpdate Tests ==============

@pytest.mark.workflows
class TestWorkflowStageUpdate:
    """Tests for WorkflowStageUpdate schema."""

    def test_stage_update_partial(self):
        """Test partial stage update."""
        data = {
            "name": "Updated Name",
            "color": "#ff0000"
        }
        stage = WorkflowStageUpdate(**data)
        assert stage.name == "Updated Name"
        assert stage.color == "#ff0000"
        assert stage.description is None


# ============== WorkflowBase Tests ==============

@pytest.mark.workflows
class TestWorkflowBase:
    """Tests for WorkflowBase schema."""

    def test_workflow_base_valid(self):
        """Test valid workflow base."""
        data = {
            "name": "Standard Pipeline",
            "description": "Our standard hiring pipeline",
            "stages": [
                {"id": "stage_1", "name": "Applied", "order": 0},
                {"id": "stage_2", "name": "Interview", "order": 1}
            ]
        }
        workflow = WorkflowBase(**data)
        assert workflow.name == "Standard Pipeline"
        assert len(workflow.stages) == 2


# ============== WorkflowCreate Tests ==============

@pytest.mark.workflows
class TestWorkflowCreate:
    """Tests for WorkflowCreate schema."""

    def test_workflow_create_valid(self):
        """Test valid workflow creation."""
        data = {
            "organization_id": "org-123",
            "name": "Engineering Pipeline",
            "is_default": True
        }
        workflow = WorkflowCreate(**data)
        assert workflow.organization_id == "org-123"
        assert workflow.is_default is True
        assert workflow.stages == []

    def test_workflow_create_with_stages(self):
        """Test workflow creation with stages."""
        data = {
            "organization_id": "org-456",
            "name": "Sales Pipeline",
            "stages": [
                {"id": "s1", "name": "Lead", "order": 0},
                {"id": "s2", "name": "Qualified", "order": 1}
            ]
        }
        workflow = WorkflowCreate(**data)
        assert len(workflow.stages) == 2


# ============== WorkflowUpdate Tests ==============

@pytest.mark.workflows
class TestWorkflowUpdate:
    """Tests for WorkflowUpdate schema."""

    def test_workflow_update_partial(self):
        """Test partial workflow update."""
        data = {
            "name": "New Name",
            "is_active": False
        }
        workflow = WorkflowUpdate(**data)
        assert workflow.name == "New Name"
        assert workflow.is_active is False
        assert workflow.stages is None


# ============== WorkflowResponse Tests ==============

@pytest.mark.workflows
class TestWorkflowResponse:
    """Tests for WorkflowResponse schema."""

    def test_workflow_response_full(self):
        """Test full workflow response."""
        data = {
            "id": "wf-123",
            "organization_id": "org-456",
            "name": "Full Pipeline",
            "description": "Complete hiring process",
            "stages": [],
            "is_default": True,
            "is_active": True,
            "created_by": "user-789",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        response = WorkflowResponse(**data)
        assert response.id == "wf-123"
        assert response.is_default is True


# ============== WorkflowListResponse Tests ==============

@pytest.mark.workflows
class TestWorkflowListResponse:
    """Tests for WorkflowListResponse schema."""

    def test_workflow_list_empty(self):
        """Test empty workflow list."""
        data = {
            "items": [],
            "total": 0,
            "page": 1,
            "page_size": 10,
            "total_pages": 0
        }
        response = WorkflowListResponse(**data)
        assert response.items == []
        assert response.total == 0


# ============== CandidateStageInfo Tests ==============

@pytest.mark.workflows
class TestCandidateStageInfo:
    """Tests for CandidateStageInfo schema."""

    def test_candidate_stage_info(self):
        """Test candidate stage info."""
        data = {
            "workflow_id": "wf-123",
            "current_stage_id": "stage_2",
            "current_stage_name": "Interview",
            "status": "active"
        }
        info = CandidateStageInfo(**data)
        assert info.current_stage_id == "stage_2"
        assert info.status == "active"


# ============== MoveCandidateRequest Tests ==============

@pytest.mark.workflows
class TestMoveCandidateRequest:
    """Tests for MoveCandidateRequest schema."""

    def test_move_candidate_valid(self):
        """Test valid move candidate request."""
        data = {
            "candidate_id": "cand-123",
            "to_stage_id": "stage_2"
        }
        request = MoveCandidateRequest(**data)
        assert request.candidate_id == "cand-123"
        assert request.skip_feedback_check is False

    def test_move_candidate_with_reason(self):
        """Test move candidate with reason."""
        data = {
            "candidate_id": "cand-456",
            "to_stage_id": "stage_3",
            "reason": "Passed technical interview",
            "skip_feedback_check": True
        }
        request = MoveCandidateRequest(**data)
        assert request.reason == "Passed technical interview"
        assert request.skip_feedback_check is True


# ============== BulkMoveCandidateRequest Tests ==============

@pytest.mark.workflows
class TestBulkMoveCandidateRequest:
    """Tests for BulkMoveCandidateRequest schema."""

    def test_bulk_move_valid(self):
        """Test valid bulk move request."""
        data = {
            "candidate_ids": ["cand-1", "cand-2", "cand-3"],
            "to_stage_id": "stage_2"
        }
        request = BulkMoveCandidateRequest(**data)
        assert len(request.candidate_ids) == 3


# ============== StageTransitionResult Tests ==============

@pytest.mark.workflows
class TestStageTransitionResult:
    """Tests for StageTransitionResult schema."""

    def test_transition_success(self):
        """Test successful transition."""
        data = {
            "success": True,
            "candidate_id": "cand-123",
            "from_stage": "stage_1",
            "to_stage": "stage_2",
            "message": "Candidate moved successfully"
        }
        result = StageTransitionResult(**data)
        assert result.success is True
        assert result.blocked_reason is None

    def test_transition_blocked(self):
        """Test blocked transition."""
        data = {
            "success": False,
            "candidate_id": "cand-456",
            "from_stage": "stage_1",
            "to_stage": "stage_2",
            "message": "Cannot move candidate",
            "blocked_reason": "Missing required feedback"
        }
        result = StageTransitionResult(**data)
        assert result.success is False
        assert result.blocked_reason == "Missing required feedback"


# ============== BulkStageTransitionResult Tests ==============

@pytest.mark.workflows
class TestBulkStageTransitionResult:
    """Tests for BulkStageTransitionResult schema."""

    def test_bulk_transition_result(self):
        """Test bulk transition result."""
        data = {
            "success": True,
            "total": 3,
            "moved": 2,
            "blocked": 1,
            "results": [],
            "message": "2 candidates moved, 1 blocked"
        }
        result = BulkStageTransitionResult(**data)
        assert result.moved == 2
        assert result.blocked == 1


# ============== InterviewerAssignmentRequest Tests ==============

@pytest.mark.workflows
class TestInterviewerAssignmentRequest:
    """Tests for InterviewerAssignmentRequest schema."""

    def test_assignment_request_valid(self):
        """Test valid assignment request."""
        data = {
            "candidate_id": "cand-123",
            "interviewer_id": "user-456",
            "duration_minutes": 60
        }
        request = InterviewerAssignmentRequest(**data)
        assert request.candidate_id == "cand-123"
        assert request.duration_minutes == 60

    def test_assignment_request_duration_limits(self):
        """Test assignment with valid duration limits."""
        data = {
            "candidate_id": "cand-123",
            "interviewer_id": "user-456",
            "duration_minutes": 480  # 8 hours max
        }
        request = InterviewerAssignmentRequest(**data)
        assert request.duration_minutes == 480

    def test_assignment_request_duration_too_short(self):
        """Test assignment with too short duration."""
        with pytest.raises(ValueError):
            InterviewerAssignmentRequest(
                candidate_id="cand-123",
                interviewer_id="user-456",
                duration_minutes=10  # Less than 15 min
            )


# ============== AssignmentResponse Tests ==============

@pytest.mark.workflows
class TestAssignmentResponse:
    """Tests for AssignmentResponse schema."""

    def test_assignment_response(self):
        """Test assignment response."""
        data = {
            "id": "assign-123",
            "candidate_id": "cand-456",
            "interviewer_id": "user-789",
            "duration_minutes": 60,
            "status": "scheduled",
            "feedback_required": True,
            "feedback_submitted": False,
            "created_at": datetime.utcnow()
        }
        response = AssignmentResponse(**data)
        assert response.id == "assign-123"
        assert response.feedback_required is True


# ============== FeedbackStatusResponse Tests ==============

@pytest.mark.workflows
class TestFeedbackStatusResponse:
    """Tests for FeedbackStatusResponse schema."""

    def test_feedback_status(self):
        """Test feedback status response."""
        data = {
            "candidate_id": "cand-123",
            "candidate_name": "John Doe",
            "current_stage_id": "stage_2",
            "current_stage_name": "Interview",
            "total_required_feedbacks": 2,
            "total_submitted_feedbacks": 1,
            "is_blocked": True,
            "blocked_reason": "Waiting for more feedback",
            "assignments": []
        }
        response = FeedbackStatusResponse(**data)
        assert response.is_blocked is True
        assert response.total_required_feedbacks == 2


# ============== PendingFeedbackResponse Tests ==============

@pytest.mark.workflows
class TestPendingFeedbackResponse:
    """Tests for PendingFeedbackResponse schema."""

    def test_pending_feedback(self):
        """Test pending feedback response."""
        data = {
            "assignment_id": "assign-123",
            "candidate_id": "cand-456",
            "candidate_name": "Jane Smith",
            "stage_id": "stage_2",
            "stage_name": "Technical",
            "interviewer_id": "user-789",
            "is_overdue": False
        }
        response = PendingFeedbackResponse(**data)
        assert response.candidate_name == "Jane Smith"
        assert response.is_overdue is False


# ============== FeedbackCompletionStats Tests ==============

@pytest.mark.workflows
class TestFeedbackCompletionStats:
    """Tests for FeedbackCompletionStats schema."""

    def test_feedback_stats(self):
        """Test feedback completion stats."""
        data = {
            "total_assignments": 10,
            "completed": 7,
            "pending": 3,
            "overdue": 1,
            "completion_rate": 0.7
        }
        stats = FeedbackCompletionStats(**data)
        assert stats.completion_rate == 0.7
        assert stats.completed == 7


# ============== DefaultWorkflowTemplate Tests ==============

@pytest.mark.workflows
class TestDefaultWorkflowTemplate:
    """Tests for DefaultWorkflowTemplate schema."""

    def test_default_template(self):
        """Test default workflow template."""
        template = DefaultWorkflowTemplate()
        assert template.name == "Standard Hiring Pipeline"
        assert template.description is not None


# ============== WorkflowTemplateResponse Tests ==============

@pytest.mark.workflows
class TestWorkflowTemplateResponse:
    """Tests for WorkflowTemplateResponse schema."""

    def test_template_response(self):
        """Test workflow template response."""
        data = {
            "name": "Quick Hire",
            "description": "Fast hiring process",
            "stages": [
                {"id": "s1", "name": "Apply", "order": 0, "description": "", 
                 "color": "#6366f1", "required_feedback_count": 0, "interview_types": []}
            ],
            "use_template": "quick_hire"
        }
        response = WorkflowTemplateResponse(**data)
        assert response.use_template == "quick_hire"


# ============== CanMoveCandidateResponse Tests ==============

@pytest.mark.workflows
class TestCanMoveCandidateResponse:
    """Tests for CanMoveCandidateResponse schema."""

    def test_can_move_response(self):
        """Test can move candidate response."""
        data = {
            "can_move": True,
            "candidate_id": "cand-123",
            "current_stage_id": "stage_1",
            "required_feedbacks": 2,
            "submitted_feedbacks": 2,
            "missing_feedbacks": []
        }
        response = CanMoveCandidateResponse(**data)
        assert response.can_move is True

    def test_cannot_move_response(self):
        """Test cannot move candidate response."""
        data = {
            "can_move": False,
            "candidate_id": "cand-456",
            "current_stage_id": "stage_1",
            "required_feedbacks": 2,
            "submitted_feedbacks": 1,
            "missing_feedbacks": ["interviewer-1"],
            "blocked_reason": "Missing required feedback"
        }
        response = CanMoveCandidateResponse(**data)
        assert response.can_move is False
        assert response.blocked_reason == "Missing required feedback"


# ============== WorkflowStageStats Tests ==============

@pytest.mark.workflows
class TestWorkflowStageStats:
    """Tests for WorkflowStageStats schema."""

    def test_stage_stats(self):
        """Test workflow stage statistics."""
        data = {
            "stage_id": "stage_1",
            "stage_name": "Application",
            "candidate_count": 10,
            "avg_time_in_stage_hours": 48.5,
            "feedback_completion_rate": 0.8
        }
        stats = WorkflowStageStats(**data)
        assert stats.candidate_count == 10
        assert stats.feedback_completion_rate == 0.8


# ============== WorkflowStatsResponse Tests ==============

@pytest.mark.workflows
class TestWorkflowStatsResponse:
    """Tests for WorkflowStatsResponse schema."""

    def test_workflow_stats(self):
        """Test workflow statistics response."""
        data = {
            "workflow_id": "wf-123",
            "total_candidates": 50,
            "active_candidates": 30,
            "completed_candidates": 15,
            "rejected_candidates": 5,
            "stage_stats": []
        }
        stats = WorkflowStatsResponse(**data)
        assert stats.total_candidates == 50
        assert stats.completed_candidates == 15

