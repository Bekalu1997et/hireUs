"""
Unit tests for Interview Kits module.
Tests interview kit schemas and validation.
"""
import pytest
from datetime import datetime
from app.schemas.interview_kit import (
    InterviewType,
    RubricCriterion,
    QuestionItem,
    InterviewKitCreate,
    InterviewKitUpdate,
    GenerateInterviewKitRequest,
    InterviewKitResponse,
    InterviewKitListResponse,
    AIGeneratedInterviewKit,
    GenerateInterviewKitResponse,
    CreateInterviewKitWithAIRequest,
    QuestionBankItem,
    QuestionBankResponse,
)


# ============== InterviewType Tests ==============

@pytest.mark.interview_kits
class TestInterviewType:
    """Tests for InterviewType enum."""

    def test_interview_type_values(self):
        """Test all interview type values."""
        assert InterviewType.CODING.value == "coding"
        assert InterviewType.SYSTEM_DESIGN.value == "system_design"
        assert InterviewType.PM_CASE.value == "pm_case"
        assert InterviewType.BEHAVIORAL.value == "behavioral"

    def test_interview_type_count(self):
        """Test correct number of interview types."""
        assert len(InterviewType) == 4


# ============== RubricCriterion Tests ==============

@pytest.mark.interview_kits
class TestRubricCriterion:
    """Tests for RubricCriterion schema."""

    def test_rubric_criterion_valid(self):
        """Test valid rubric criterion."""
        data = {
            "name": "Code Quality",
            "description": "Evaluates code quality and best practices",
            "max_score": 5,
            "weight": 2
        }
        criterion = RubricCriterion(**data)
        assert criterion.name == "Code Quality"
        assert criterion.max_score == 5
        assert criterion.weight == 2

    def test_rubric_criterion_defaults(self):
        """Test rubric criterion with defaults."""
        data = {
            "name": "Communication",
            "description": "How well they communicate"
        }
        criterion = RubricCriterion(**data)
        assert criterion.max_score == 5
        assert criterion.weight == 1

    def test_rubric_criterion_max_score_limits(self):
        """Test rubric criterion max score validation."""
        with pytest.raises(ValueError):
            RubricCriterion(name="Test", description="Desc", max_score=11)

    def test_rubric_criterion_weight_limits(self):
        """Test rubric criterion weight validation."""
        with pytest.raises(ValueError):
            RubricCriterion(name="Test", description="Desc", weight=6)


# ============== QuestionItem Tests ==============

@pytest.mark.interview_kits
class TestQuestionItem:
    """Tests for QuestionItem schema."""

    def test_question_item_valid(self):
        """Test valid question item."""
        data = {
            "question": "Implement a binary search",
            "type": "coding",
            "duration_minutes": 15,
            "difficulty": "medium"
        }
        question = QuestionItem(**data)
        assert question.question == "Implement a binary search"
        assert question.type == "coding"

    def test_question_item_defaults(self):
        """Test question item with defaults."""
        data = {"question": "Tell me about yourself"}
        question = QuestionItem(**data)
        assert question.type == "open-ended"
        assert question.difficulty == "medium"
        assert question.duration_minutes == 10


# ============== InterviewKitCreate Tests ==============

@pytest.mark.interview_kits
class TestInterviewKitCreate:
    """Tests for InterviewKitCreate schema."""

    def test_kit_create_valid(self):
        """Test valid interview kit creation."""
        data = {
            "organization_id": "org-123",
            "title": "Python Coding Interview",
            "type": "coding",
            "estimated_duration_minutes": 60
        }
        kit = InterviewKitCreate(**data)
        assert kit.organization_id == "org-123"
        assert kit.title == "Python Coding Interview"
        assert kit.type == "coding"

    def test_kit_create_with_role(self):
        """Test interview kit creation with role."""
        data = {
            "organization_id": "org-456",
            "role_id": "role-789",
            "title": "System Design Interview",
            "type": "system_design"
        }
        kit = InterviewKitCreate(**data)
        assert kit.role_id == "role-789"

    def test_kit_create_with_rubric(self):
        """Test interview kit creation with evaluation rubric."""
        data = {
            "organization_id": "org-123",
            "title": "Behavioral Interview",
            "type": "behavioral",
            "evaluation_rubric": [
                {"name": "Communication", "description": "Clarity", "max_score": 5}
            ]
        }
        kit = InterviewKitCreate(**data)
        assert len(kit.evaluation_rubric) == 1


# ============== InterviewKitUpdate Tests ==============

@pytest.mark.interview_kits
class TestInterviewKitUpdate:
    """Tests for InterviewKitUpdate schema."""

    def test_kit_update_partial(self):
        """Test partial interview kit update."""
        data = {
            "title": "Updated Title",
            "is_active": False
        }
        kit = InterviewKitUpdate(**data)
        assert kit.title == "Updated Title"
        assert kit.is_active is False
        assert kit.description is None


# ============== GenerateInterviewKitRequest Tests ==============

@pytest.mark.interview_kits
class TestGenerateInterviewKitRequest:
    """Tests for GenerateInterviewKitRequest schema."""

    def test_generate_request_valid(self):
        """Test valid generation request."""
        data = {
            "role_title": "Senior Python Developer",
            "seniority": "senior",
            "interview_type": "coding",
            "duration_minutes": 60
        }
        request = GenerateInterviewKitRequest(**data)
        assert request.role_title == "Senior Python Developer"
        assert request.seniority == "senior"
        assert request.stack == []

    def test_generate_request_with_stack(self):
        """Test generation request with tech stack."""
        data = {
            "role_title": "Backend Developer",
            "seniority": "mid",
            "stack": ["Python", "Django", "PostgreSQL"],
            "interview_type": "coding"
        }
        request = GenerateInterviewKitRequest(**data)
        assert len(request.stack) == 3


# ============== InterviewKitResponse Tests ==============

@pytest.mark.interview_kits
class TestInterviewKitResponse:
    """Tests for InterviewKitResponse schema."""

    def test_kit_response_full(self):
        """Test full interview kit response."""
        data = {
            "id": "kit-123",
            "organization_id": "org-456",
            "role_id": "role-789",
            "title": "Full Stack Interview",
            "type": "coding",
            "description": "Comprehensive coding interview",
            "estimated_duration_minutes": 90,
            "version": 1,
            "is_template": False,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        response = InterviewKitResponse(**data)
        assert response.id == "kit-123"
        assert response.version == 1


# ============== InterviewKitListResponse Tests ==============

@pytest.mark.interview_kits
class TestInterviewKitListResponse:
    """Tests for InterviewKitListResponse schema."""

    def test_kit_list_empty(self):
        """Test empty interview kit list."""
        data = {
            "items": [],
            "total": 0,
            "page": 1,
            "page_size": 10,
            "total_pages": 0
        }
        response = InterviewKitListResponse(**data)
        assert response.items == []
        assert response.total == 0


# ============== AIGeneratedInterviewKit Tests ==============

@pytest.mark.interview_kits
class TestAIGeneratedInterviewKit:
    """Tests for AIGeneratedInterviewKit schema."""

    def test_ai_kit_valid(self):
        """Test valid AI generated kit."""
        data = {
            "title": "AI Generated Coding Interview",
            "problem_statement": "Implement a LRU Cache",
            "evaluation_rubric": [{"name": "Complexity", "description": "Time and space"}],
            "red_flags": ["Copying code from internet"],
            "good_answer_outline": "Step 1: Design, Step 2: Implement",
            "questions": []
        }
        kit = AIGeneratedInterviewKit(**data)
        assert kit.title == "AI Generated Coding Interview"
        assert len(kit.red_flags) == 1

    def test_ai_kit_with_tips(self):
        """Test AI kit with tips."""
        data = {
            "title": "Test Kit",
            "problem_statement": "Problem",
            "evaluation_rubric": [],
            "red_flags": [],
            "good_answer_outline": "Answer",
            "tips_for_interviewer": "Look for clean code"
        }
        kit = AIGeneratedInterviewKit(**data)
        assert "clean code" in kit.tips_for_interviewer


# ============== GenerateInterviewKitResponse Tests ==============

@pytest.mark.interview_kits
class TestGenerateInterviewKitResponse:
    """Tests for GenerateInterviewKitResponse schema."""

    def test_generation_success(self):
        """Test successful kit generation response."""
        data = {
            "success": True,
            "kit": {
                "title": "Generated Kit",
                "problem_statement": "Problem",
                "evaluation_rubric": [],
                "red_flags": [],
                "good_answer_outline": "Answer"
            }
        }
        response = GenerateInterviewKitResponse(**data)
        assert response.success is True
        assert response.kit is not None

    def test_generation_error(self):
        """Test error in kit generation response."""
        data = {
            "success": False,
            "error": "API rate limit exceeded"
        }
        response = GenerateInterviewKitResponse(**data)
        assert response.success is False
        assert response.error == "API rate limit exceeded"
        assert response.kit is None


# ============== CreateInterviewKitWithAIRequest Tests ==============

@pytest.mark.interview_kits
class TestCreateInterviewKitWithAIRequest:
    """Tests for CreateInterviewKitWithAIRequest schema."""

    def test_create_ai_request_valid(self):
        """Test valid create with AI request."""
        data = {
            "organization_id": "org-123",
            "role_title": "ML Engineer",
            "seniority": "senior",
            "interview_type": "coding",
            "competencies": ["Python", "Machine Learning"]
        }
        request = CreateInterviewKitWithAIRequest(**data)
        assert request.organization_id == "org-123"
        assert len(request.competencies) == 2


# ============== QuestionBankItem Tests ==============

@pytest.mark.interview_kits
class TestQuestionBankItem:
    """Tests for QuestionBankItem schema."""

    def test_question_bank_item(self):
        """Test question bank item."""
        data = {
            "id": "q-123",
            "interview_kit_id": "kit-456",
            "question": "What is a linked list?",
            "type": "open-ended",
            "duration_minutes": 5,
            "difficulty": "easy",
            "is_active": True,
            "created_at": datetime.utcnow()
        }
        item = QuestionBankItem(**data)
        assert item.id == "q-123"
        assert item.difficulty == "easy"


# ============== QuestionBankResponse Tests ==============

@pytest.mark.interview_kits
class TestQuestionBankResponse:
    """Tests for QuestionBankResponse schema."""

    def test_question_bank_response(self):
        """Test question bank response."""
        data = {
            "items": [],
            "total": 0
        }
        response = QuestionBankResponse(**data)
        assert response.total == 0

