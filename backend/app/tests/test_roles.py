"""
Unit tests for Roles module.
Tests role schemas, validation, and enums.
"""
import pytest
from datetime import datetime
from app.schemas.role import (
    RoleCreateInput,
    RoleUpdateInput,
    RoleBlueprintGenerateInput,
    RoleCreate,
    RoleUpdate,
    RoleResponse,
    RoleListResponse,
    RoleBlueprintResponse,
    GenerateBlueprintRequest,
    GenerateBlueprintResponse,
    SeniorityLevel,
    InterviewType,
    CompetencyResponse,
    InterviewStageResponse,
    AIGeneratedBlueprint,
)


# ============== SeniorityLevel Tests ==============

@pytest.mark.roles
class TestSeniorityLevel:
    """Tests for SeniorityLevel enum."""

    def test_seniority_level_values(self):
        """Test all seniority level values exist."""
        assert SeniorityLevel.INTERN.value == "intern"
        assert SeniorityLevel.JUNIOR.value == "junior"
        assert SeniorityLevel.MID.value == "mid"
        assert SeniorityLevel.SENIOR.value == "senior"
        assert SeniorityLevel.LEAD.value == "lead"
        assert SeniorityLevel.PRINCIPAL.value == "principal"
        assert SeniorityLevel.DIRECTOR.value == "director"
        assert SeniorityLevel.VP.value == "vp"

    def test_seniority_level_count(self):
        """Test correct number of seniority levels."""
        assert len(SeniorityLevel) == 8


# ============== InterviewType Tests ==============

@pytest.mark.roles
class TestInterviewType:
    """Tests for InterviewType enum."""

    def test_interview_type_values(self):
        """Test all interview type values exist."""
        assert InterviewType.CODING.value == "coding"
        assert InterviewType.SYSTEM_DESIGN.value == "system_design"
        assert InterviewType.BEHAVIORAL.value == "behavioral"
        assert InterviewType.CULTURE_FIT.value == "culture_fit"
        assert InterviewType.TECHNICAL_SCREEN.value == "technical_screen"
        assert InterviewType.FINAL_ROUND.value == "final_round"

    def test_interview_type_count(self):
        """Test correct number of interview types."""
        assert len(InterviewType) == 6


# ============== RoleCreateInput Tests ==============

@pytest.mark.roles
class TestRoleCreateInput:
    """Tests for RoleCreateInput schema."""

    def test_role_create_input_valid(self):
        """Test valid role create input."""
        data = {
            "title": "Senior Python Developer",
            "seniority": "senior",
            "department": "Engineering",
            "tech_stack": ["Python", "Django", "PostgreSQL"],
            "team_context": "Backend team"
        }
        role = RoleCreateInput(**data)
        assert role.title == "Senior Python Developer"
        assert role.seniority == "senior"
        assert role.department == "Engineering"
        assert len(role.tech_stack) == 3

    def test_role_create_input_minimal(self):
        """Test role create input with minimal data."""
        data = {
            "title": "Developer",
            "seniority": "mid"
        }
        role = RoleCreateInput(**data)
        assert role.title == "Developer"
        assert role.seniority == "mid"
        assert role.tech_stack == []

    def test_role_create_input_title_too_short(self):
        """Test role create input with empty title."""
        with pytest.raises(ValueError):
            RoleCreateInput(title="", seniority="senior")

    def test_role_create_input_title_too_long(self):
        """Test role create input with title exceeding max length."""
        with pytest.raises(ValueError):
            RoleCreateInput(title="a" * 256, seniority="senior")

    def test_role_create_input_empty_tech_stack(self):
        """Test role create input with empty tech stack."""
        data = {
            "title": "Developer",
            "seniority": "junior",
            "tech_stack": []
        }
        role = RoleCreateInput(**data)
        assert role.tech_stack == []


# ============== RoleUpdateInput Tests ==============

@pytest.mark.roles
class TestRoleUpdateInput:
    """Tests for RoleUpdateInput schema."""

    def test_role_update_input_partial(self):
        """Test role update input with partial data."""
        data = {
            "title": "Updated Title",
            "is_active": False
        }
        role = RoleUpdateInput(**data)
        assert role.title == "Updated Title"
        assert role.is_active is False
        assert role.description is None

    def test_role_update_input_empty(self):
        """Test role update input with no data."""
        role = RoleUpdateInput()
        assert role.title is None

    def test_role_update_input_with_lists(self):
        """Test role update input with list fields."""
        data = {
            "tech_stack": ["Python", "FastAPI"],
            "core_competencies": [{"name": "API Design", "weight": "must-have"}],
            "interview_stages": [{"name": "Phone Screen", "duration": 30}]
        }
        role = RoleUpdateInput(**data)
        assert len(role.tech_stack) == 2
        assert len(role.core_competencies) == 1


# ============== RoleBlueprintGenerateInput Tests ==============

@pytest.mark.roles
class TestRoleBlueprintGenerateInput:
    """Tests for RoleBlueprintGenerateInput schema."""

    def test_blueprint_input_valid(self):
        """Test valid blueprint generation input."""
        data = {
            "title": "ML Engineer",
            "seniority": "senior",
            "stack": ["Python", "TensorFlow", "PyTorch"],
            "team_context": "AI/ML team"
        }
        blueprint = RoleBlueprintGenerateInput(**data)
        assert blueprint.title == "ML Engineer"
        assert blueprint.seniority == "senior"
        assert len(blueprint.stack) == 3

    def test_blueprint_input_default_stack(self):
        """Test blueprint input with default empty stack."""
        data = {
            "title": "Developer",
            "seniority": "junior"
        }
        blueprint = RoleBlueprintGenerateInput(**data)
        assert blueprint.stack == []


# ============== GenerateBlueprintRequest Tests ==============

@pytest.mark.roles
class TestGenerateBlueprintRequest:
    """Tests for GenerateBlueprintRequest schema."""

    def test_generate_request_valid(self):
        """Test valid blueprint generation request."""
        data = {
            "title": "Backend Developer",
            "seniority": "senior",
            "stack": ["Python", "Go"],
            "team_context": " microservices team"
        }
        request = GenerateBlueprintRequest(**data)
        assert request.title == "Backend Developer"
        assert request.seniority == "senior"


# ============== CompetencyResponse Tests ==============

@pytest.mark.roles
class TestCompetencyResponse:
    """Tests for CompetencyResponse schema."""

    def test_competency_response_valid(self):
        """Test valid competency response."""
        data = {
            "name": "Python",
            "description": "Proficiency in Python",
            "weight": "must-have"
        }
        competency = CompetencyResponse(**data)
        assert competency.name == "Python"
        assert competency.weight == "must-have"

    def test_competency_response_default_weight(self):
        """Test competency with default weight."""
        data = {
            "name": "Communication",
            "description": "Good communication skills"
        }
        competency = CompetencyResponse(**data)
        assert competency.weight == "must-have"


# ============== InterviewStageResponse Tests ==============

@pytest.mark.roles
class TestInterviewStageResponse:
    """Tests for InterviewStageResponse schema."""

    def test_interview_stage_valid(self):
        """Test valid interview stage."""
        data = {
            "name": "Technical Interview",
            "duration_minutes": 60,
            "description": "Coding challenge",
            "interview_type": "coding"
        }
        stage = InterviewStageResponse(**data)
        assert stage.name == "Technical Interview"
        assert stage.duration_minutes == 60

    def test_interview_stage_default_duration(self):
        """Test interview stage with default duration."""
        data = {
            "name": "Culture Fit",
            "description": "Team interview",
            "interview_type": "behavioral"
        }
        stage = InterviewStageResponse(**data)
        assert stage.duration_minutes == 60


# ============== RoleBlueprintResponse Tests ==============

@pytest.mark.roles
class TestRoleBlueprintResponse:
    """Tests for RoleBlueprintResponse schema."""

    def test_blueprint_response_valid(self):
        """Test valid role blueprint response."""
        data = {
            "mission": "Build great products",
            "competencies": [
                {"name": "Python", "description": "Skill", "weight": "must-have"}
            ],
            "must_have": {"skills": ["Python"]},
            "nice_to_have": {"skills": ["AWS"]},
            "interview_stages": [
                {
                    "name": "Tech Screen",
                    "duration_minutes": 45,
                    "description": "Phone interview",
                    "interview_type": "technical_screen"
                }
            ]
        }
        blueprint = RoleBlueprintResponse(**data)
        assert blueprint.mission == "Build great products"
        assert len(blueprint.competencies) == 1
        assert len(blueprint.interview_stages) == 1


# ============== AIGeneratedBlueprint Tests ==============

@pytest.mark.roles
class TestAIGeneratedBlueprint:
    """Tests for AIGeneratedBlueprint schema."""

    def test_ai_blueprint_valid(self):
        """Test valid AI generated blueprint."""
        data = {
            "mission": "Lead technical initiatives",
            "competencies": [{"name": "Leadership"}],
            "must_have": {"experience": 5},
            "nice_to_have": {"certifications": ["AWS"]},
            "interview_stages": []
        }
        blueprint = AIGeneratedBlueprint(**data)
        assert blueprint.mission == "Lead technical initiatives"

    def test_ai_blueprint_empty_arrays(self):
        """Test AI blueprint with empty arrays."""
        data = {
            "mission": "Test mission",
            "competencies": [],
            "must_have": {},
            "nice_to_have": {},
            "interview_stages": []
        }
        blueprint = AIGeneratedBlueprint(**data)
        assert blueprint.competencies == []
        assert blueprint.interview_stages == []


# ============== GenerateBlueprintResponse Tests ==============

@pytest.mark.roles
class TestGenerateBlueprintResponse:
    """Tests for GenerateBlueprintResponse schema."""

    def test_blueprint_response_success(self):
        """Test successful blueprint generation response."""
        data = {
            "success": True,
            "blueprint": {
                "mission": "Build AI",
                "competencies": [{"name": "ML"}],
                "must_have": {},
                "nice_to_have": {},
                "interview_stages": []
            },
            "model_used": "gemini-pro"
        }
        response = GenerateBlueprintResponse(**data)
        assert response.success is True
        assert response.blueprint is not None
        assert response.model_used == "gemini-pro"

    def test_blueprint_response_error(self):
        """Test error blueprint generation response."""
        data = {
            "success": False,
            "error": "API rate limit exceeded",
            "model_used": "gemini-pro"
        }
        response = GenerateBlueprintResponse(**data)
        assert response.success is False
        assert response.error == "API rate limit exceeded"
        assert response.blueprint is None


# ============== RoleCreate/Update DB Schema Tests ==============

@pytest.mark.roles
class TestRoleDatabaseSchemas:
    """Tests for role database schemas."""

    def test_role_create_with_defaults(self):
        """Test RoleCreate with default values."""
        data = {
            "organization_id": "org-123",
            "title": "Developer",
            "tech_stack": ["Python"]
        }
        role = RoleCreate(**data)
        assert role.tech_stack == ["Python"]
        assert role.core_competencies == []
        assert role.must_have == {}
        assert role.nice_to_have == {}

    def test_role_update_inherits_base(self):
        """Test RoleUpdate inherits from RoleBase."""
        data = {
            "title": "Senior Developer",
            "description": "Great role",
            "seniority": "senior"
        }
        role = RoleUpdate(**data)
        assert role.title == "Senior Developer"
        assert role.description == "Great role"


# ============== Role List Response Tests ==============

@pytest.mark.roles
class TestRoleListResponse:
    """Tests for RoleListResponse schema."""

    def test_role_list_response_empty(self):
        """Test empty role list response."""
        data = {
            "items": [],
            "total": 0,
            "page": 1,
            "page_size": 10,
            "total_pages": 0
        }
        response = RoleListResponse(**data)
        assert response.items == []
        assert response.total == 0

    def test_role_list_response_pagination(self):
        """Test role list response pagination."""
        data = {
            "items": [
                {"id": "1", "organization_id": "org-1", "title": "Dev", 
                 "slug": "dev", "tech_stack": [], "core_competencies": [],
                 "interview_stages": [], "must_have": {}, "nice_to_have": {},
                 "is_active": True, "created_at": datetime.utcnow(), 
                 "updated_at": datetime.utcnow()}
            ],
            "total": 1,
            "page": 1,
            "page_size": 10,
            "total_pages": 1
        }
        response = RoleListResponse(**data)
        assert len(response.items) == 1
        assert response.total_pages == 1


# ============== Role Response Schema Tests ==============

@pytest.mark.roles
class TestRoleResponse:
    """Tests for RoleResponse schema."""

    def test_role_response_full(self):
        """Test full role response."""
        data = {
            "id": "role-123",
            "organization_id": "org-456",
            "title": "Python Developer",
            "slug": "python-developer",
            "description": "Great opportunity",
            "seniority": "senior",
            "department": "Engineering",
            "tech_stack": ["Python", "Django"],
            "core_competencies": [{"name": "Backend"}],
            "interview_stages": [{"name": "Tech Screen"}],
            "mission": "Build products",
            "must_have": {"skills": ["Python"]},
            "nice_to_have": {"skills": ["AWS"]},
            "is_active": True,
            "created_by": "user-123",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        response = RoleResponse(**data)
        assert response.id == "role-123"
        assert response.slug == "python-developer"
        assert response.is_active is True

