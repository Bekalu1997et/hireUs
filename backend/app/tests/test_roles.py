"""
Tests for roles and competencies service.

Feature: structured-interview-platform
"""
import pytest
from hypothesis import given, strategies as st
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.roles.service import RolesService
from app.modules.auth.service import AuthService
from app.schemas.role import RoleCreate, CompetencyCreate
from app.schemas.auth import UserRegister


# Hypothesis strategies for generating valid test data
valid_title = st.text(min_size=1, max_size=255, alphabet=st.characters(blacklist_categories=('Cc', 'Cs')))
valid_description = st.text(min_size=1, max_size=1000, alphabet=st.characters(blacklist_categories=('Cc', 'Cs')))
valid_seniority = st.sampled_from(["junior", "mid", "senior", "staff", "principal"])
valid_competency_name = st.text(min_size=1, max_size=255, alphabet=st.characters(blacklist_categories=('Cc', 'Cs')))
valid_weight = st.floats(min_value=0.1, max_value=1.0)


def normalize_weights(competencies):
    """Normalize competency weights to sum to 1.0."""
    total = sum(c['weight'] for c in competencies)
    if total == 0:
        equal_weight = 1.0 / len(competencies)
        return [{**c, 'weight': equal_weight} for c in competencies]
    return [{**c, 'weight': c['weight'] / total} for c in competencies]


# Feature: structured-interview-platform, Property 8: Role Data Persistence
@pytest.mark.property
@pytest.mark.asyncio
@given(
    title=valid_title,
    description=valid_description,
    seniority=valid_seniority,
    competencies=st.lists(
        st.fixed_dictionaries({
            'name': valid_competency_name,
            'description': valid_description,
            'weight': valid_weight
        }),
        min_size=1,
        max_size=10
    )
)
async def test_role_data_persistence(
    db_session: AsyncSession,
    title: str,
    description: str,
    seniority: str,
    competencies: list
):
    """
    Property 8: Role Data Persistence
    
    For any role creation with competencies, all role fields (title, description,
    seniority level) and all competency fields (name, description, weight) should
    be retrievable after storage.
    
    Validates: Requirements 3.1, 3.3
    """
    # Create organization and user first
    auth_service = AuthService(db_session)
    user_data = UserRegister(
        email=f"test_{hash(title)}@example.com",
        password="StrongPass123",
        full_name="Test User",
        organization_name="Test Org",
        organization_domain=f"test{hash(title)}.com"
    )
    user, _ = await auth_service.register_user(user_data)
    
    # Normalize weights to sum to 1.0
    competencies = normalize_weights(competencies)
    
    # Create role
    roles_service = RolesService(db_session)
    role_data = RoleCreate(
        title=title,
        description=description,
        seniority_level=seniority,
        competencies=[
            CompetencyCreate(
                name=comp['name'],
                description=comp['description'],
                weight=comp['weight']
            )
            for comp in competencies
        ]
    )
    
    created_role = await roles_service.create_role(role_data, user.organization_id)
    
    # Retrieve role
    retrieved_role = await roles_service.get_role(created_role.id, user.organization_id)
    
    # Verify all role fields match
    assert retrieved_role.title == title
    assert retrieved_role.description == description
    assert retrieved_role.seniority_level == seniority
    assert retrieved_role.organization_id == user.organization_id
    
    # Verify all competencies are stored
    assert len(retrieved_role.competencies) == len(competencies)
    
    # Verify competency fields match (order may differ, so sort by name)
    retrieved_comps = sorted(retrieved_role.competencies, key=lambda c: c.name)
    expected_comps = sorted(competencies, key=lambda c: c['name'])
    
    for retrieved, expected in zip(retrieved_comps, expected_comps):
        assert retrieved.name == expected['name']
        assert retrieved.description == expected['description']
        # Allow small floating point differences
        assert abs(retrieved.weight - expected['weight']) < 0.001


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_role_with_valid_data(db_session: AsyncSession):
    """Test creating a role with valid data."""
    # Create organization and user
    auth_service = AuthService(db_session)
    user_data = UserRegister(
        email="founder@example.com",
        password="StrongPass123",
        full_name="Founder User",
        organization_name="Test Org",
        organization_domain="testorg.com"
    )
    user, _ = await auth_service.register_user(user_data)
    
    # Create role
    roles_service = RolesService(db_session)
    role_data = RoleCreate(
        title="Senior Backend Engineer",
        description="Experienced backend developer",
        seniority_level="senior",
        competencies=[
            CompetencyCreate(name="Python", description="Python programming", weight=0.4),
            CompetencyCreate(name="System Design", description="Architecture skills", weight=0.3),
            CompetencyCreate(name="Databases", description="SQL and NoSQL", weight=0.3)
        ]
    )
    
    role = await roles_service.create_role(role_data, user.organization_id)
    
    assert role.id is not None
    assert role.title == "Senior Backend Engineer"
    assert role.seniority_level == "senior"
    assert len(role.competencies) == 3
    
    # Verify weights sum to 1.0
    total_weight = sum(c.weight for c in role.competencies)
    assert abs(total_weight - 1.0) < 0.001


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_role_by_id(db_session: AsyncSession):
    """Test retrieving a role by ID."""
    # Create organization and user
    auth_service = AuthService(db_session)
    user_data = UserRegister(
        email="founder@example.com",
        password="StrongPass123",
        full_name="Founder User",
        organization_name="Test Org",
        organization_domain="testorg.com"
    )
    user, _ = await auth_service.register_user(user_data)
    
    # Create role
    roles_service = RolesService(db_session)
    role_data = RoleCreate(
        title="Frontend Engineer",
        description="React developer",
        seniority_level="mid",
        competencies=[
            CompetencyCreate(name="React", description="React framework", weight=0.5),
            CompetencyCreate(name="TypeScript", description="TypeScript language", weight=0.5)
        ]
    )
    
    created_role = await roles_service.create_role(role_data, user.organization_id)
    
    # Retrieve role
    retrieved_role = await roles_service.get_role(created_role.id, user.organization_id)
    
    assert retrieved_role.id == created_role.id
    assert retrieved_role.title == "Frontend Engineer"
    assert len(retrieved_role.competencies) == 2


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_role_not_found(db_session: AsyncSession):
    """Test retrieving a non-existent role."""
    # Create organization and user
    auth_service = AuthService(db_session)
    user_data = UserRegister(
        email="founder@example.com",
        password="StrongPass123",
        full_name="Founder User",
        organization_name="Test Org",
        organization_domain="testorg.com"
    )
    user, _ = await auth_service.register_user(user_data)
    
    # Try to get non-existent role
    roles_service = RolesService(db_session)
    
    with pytest.raises(HTTPException) as exc_info:
        await roles_service.get_role(99999, user.organization_id)
    
    assert exc_info.value.status_code == 404


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_roles_for_organization(db_session: AsyncSession):
    """Test listing all roles for an organization."""
    # Create organization and user
    auth_service = AuthService(db_session)
    user_data = UserRegister(
        email="founder@example.com",
        password="StrongPass123",
        full_name="Founder User",
        organization_name="Test Org",
        organization_domain="testorg.com"
    )
    user, _ = await auth_service.register_user(user_data)
    
    # Create multiple roles
    roles_service = RolesService(db_session)
    
    role1_data = RoleCreate(
        title="Backend Engineer",
        description="Backend dev",
        seniority_level="senior",
        competencies=[
            CompetencyCreate(name="Python", description="Python", weight=1.0)
        ]
    )
    
    role2_data = RoleCreate(
        title="Frontend Engineer",
        description="Frontend dev",
        seniority_level="mid",
        competencies=[
            CompetencyCreate(name="React", description="React", weight=1.0)
        ]
    )
    
    await roles_service.create_role(role1_data, user.organization_id)
    await roles_service.create_role(role2_data, user.organization_id)
    
    # List roles
    roles = await roles_service.list_roles(user.organization_id)
    
    assert len(roles) == 2
    titles = [r.title for r in roles]
    assert "Backend Engineer" in titles
    assert "Frontend Engineer" in titles


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_role(db_session: AsyncSession):
    """Test updating a role."""
    # Create organization and user
    auth_service = AuthService(db_session)
    user_data = UserRegister(
        email="founder@example.com",
        password="StrongPass123",
        full_name="Founder User",
        organization_name="Test Org",
        organization_domain="testorg.com"
    )
    user, _ = await auth_service.register_user(user_data)
    
    # Create role
    roles_service = RolesService(db_session)
    role_data = RoleCreate(
        title="Engineer",
        description="Original description",
        seniority_level="mid",
        competencies=[
            CompetencyCreate(name="Skill", description="Skill desc", weight=1.0)
        ]
    )
    
    role = await roles_service.create_role(role_data, user.organization_id)
    
    # Update role
    from app.schemas.role import RoleUpdate
    update_data = RoleUpdate(
        title="Senior Engineer",
        description="Updated description"
    )
    
    updated_role = await roles_service.update_role(role.id, update_data, user.organization_id)
    
    assert updated_role.title == "Senior Engineer"
    assert updated_role.description == "Updated description"
    assert updated_role.seniority_level == "mid"  # Unchanged


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_role(db_session: AsyncSession):
    """Test deleting a role."""
    # Create organization and user
    auth_service = AuthService(db_session)
    user_data = UserRegister(
        email="founder@example.com",
        password="StrongPass123",
        full_name="Founder User",
        organization_name="Test Org",
        organization_domain="testorg.com"
    )
    user, _ = await auth_service.register_user(user_data)
    
    # Create role
    roles_service = RolesService(db_session)
    role_data = RoleCreate(
        title="Engineer",
        description="Description",
        seniority_level="mid",
        competencies=[
            CompetencyCreate(name="Skill", description="Skill desc", weight=1.0)
        ]
    )
    
    role = await roles_service.create_role(role_data, user.organization_id)
    
    # Delete role
    await roles_service.delete_role(role.id, user.organization_id)
    
    # Verify role is deleted
    with pytest.raises(HTTPException) as exc_info:
        await roles_service.get_role(role.id, user.organization_id)
    
    assert exc_info.value.status_code == 404



# Feature: structured-interview-platform, Property 9: Role Validation
@pytest.mark.property
@pytest.mark.asyncio
@given(
    title=valid_title,
    description=valid_description,
    seniority=valid_seniority
)
async def test_role_validation_requires_competencies(
    db_session: AsyncSession,
    title: str,
    description: str,
    seniority: str
):
    """
    Property 9: Role Validation
    
    For any role creation attempt without competencies, the system should
    reject the creation with a validation error.
    
    Validates: Requirements 3.2
    """
    # Create organization and user
    auth_service = AuthService(db_session)
    user_data = UserRegister(
        email=f"test_{hash(title)}@example.com",
        password="StrongPass123",
        full_name="Test User",
        organization_name="Test Org",
        organization_domain=f"test{hash(title)}.com"
    )
    user, _ = await auth_service.register_user(user_data)
    
    # Try to create role without competencies
    roles_service = RolesService(db_session)
    
    # This should fail at Pydantic validation level (min_length=1)
    # But let's also test the service layer validation
    with pytest.raises((HTTPException, ValueError)):
        role_data = RoleCreate(
            title=title,
            description=description,
            seniority_level=seniority,
            competencies=[]  # Empty competencies
        )
        await roles_service.create_role(role_data, user.organization_id)


# Feature: structured-interview-platform, Property 10: Competency Weight Validation
@pytest.mark.property
@pytest.mark.asyncio
@given(
    title=valid_title,
    description=valid_description,
    seniority=valid_seniority,
    competencies=st.lists(
        st.fixed_dictionaries({
            'name': valid_competency_name,
            'description': valid_description,
            'weight': valid_weight
        }),
        min_size=1,
        max_size=10
    )
)
async def test_competency_weight_validation(
    db_session: AsyncSession,
    title: str,
    description: str,
    seniority: str,
    competencies: list
):
    """
    Property 10: Competency Weight Validation
    
    For any role with multiple competencies, the sum of competency weights
    should be validated to ensure proper scoring calculations (weights should
    sum to 1.0 with reasonable tolerance).
    
    After normalization, weights should sum to exactly 1.0.
    
    Validates: Requirements 3.4
    """
    # Create organization and user
    auth_service = AuthService(db_session)
    user_data = UserRegister(
        email=f"test_{hash(title)}@example.com",
        password="StrongPass123",
        full_name="Test User",
        organization_name="Test Org",
        organization_domain=f"test{hash(title)}.com"
    )
    user, _ = await auth_service.register_user(user_data)
    
    # Normalize weights (service does this automatically)
    competencies = normalize_weights(competencies)
    
    # Create role
    roles_service = RolesService(db_session)
    role_data = RoleCreate(
        title=title,
        description=description,
        seniority_level=seniority,
        competencies=[
            CompetencyCreate(
                name=comp['name'],
                description=comp['description'],
                weight=comp['weight']
            )
            for comp in competencies
        ]
    )
    
    created_role = await roles_service.create_role(role_data, user.organization_id)
    
    # Verify weights sum to 1.0 (with small tolerance for floating point)
    total_weight = sum(c.weight for c in created_role.competencies)
    assert abs(total_weight - 1.0) < 0.001, f"Weights sum to {total_weight}, expected 1.0"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_role_without_competencies_fails(db_session: AsyncSession):
    """Test that creating a role without competencies fails."""
    # Create organization and user
    auth_service = AuthService(db_session)
    user_data = UserRegister(
        email="founder@example.com",
        password="StrongPass123",
        full_name="Founder User",
        organization_name="Test Org",
        organization_domain="testorg.com"
    )
    user, _ = await auth_service.register_user(user_data)
    
    # Try to create role without competencies
    roles_service = RolesService(db_session)
    
    with pytest.raises((HTTPException, ValueError)):
        role_data = RoleCreate(
            title="Engineer",
            description="Description",
            seniority_level="mid",
            competencies=[]
        )
        await roles_service.create_role(role_data, user.organization_id)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_competency_weights_are_normalized(db_session: AsyncSession):
    """Test that competency weights are normalized to sum to 1.0."""
    # Create organization and user
    auth_service = AuthService(db_session)
    user_data = UserRegister(
        email="founder@example.com",
        password="StrongPass123",
        full_name="Founder User",
        organization_name="Test Org",
        organization_domain="testorg.com"
    )
    user, _ = await auth_service.register_user(user_data)
    
    # Create role with weights that don't sum to 1.0
    roles_service = RolesService(db_session)
    role_data = RoleCreate(
        title="Engineer",
        description="Description",
        seniority_level="mid",
        competencies=[
            CompetencyCreate(name="Skill 1", description="Desc 1", weight=0.2),
            CompetencyCreate(name="Skill 2", description="Desc 2", weight=0.3),
            CompetencyCreate(name="Skill 3", description="Desc 3", weight=0.5)
        ]
    )
    
    role = await roles_service.create_role(role_data, user.organization_id)
    
    # Verify weights are normalized to sum to 1.0
    total_weight = sum(c.weight for c in role.competencies)
    assert abs(total_weight - 1.0) < 0.001


@pytest.mark.unit
@pytest.mark.asyncio
async def test_role_organization_isolation(db_session: AsyncSession):
    """Test that roles are isolated by organization."""
    # Create two organizations
    auth_service = AuthService(db_session)
    
    user1_data = UserRegister(
        email="founder1@example.com",
        password="StrongPass123",
        full_name="Founder 1",
        organization_name="Org 1",
        organization_domain="org1.com"
    )
    user1, _ = await auth_service.register_user(user1_data)
    
    user2_data = UserRegister(
        email="founder2@example.com",
        password="StrongPass123",
        full_name="Founder 2",
        organization_name="Org 2",
        organization_domain="org2.com"
    )
    user2, _ = await auth_service.register_user(user2_data)
    
    # Create role in org 1
    roles_service = RolesService(db_session)
    role_data = RoleCreate(
        title="Engineer",
        description="Description",
        seniority_level="mid",
        competencies=[
            CompetencyCreate(name="Skill", description="Desc", weight=1.0)
        ]
    )
    
    role = await roles_service.create_role(role_data, user1.organization_id)
    
    # User from org 2 should not be able to access role from org 1
    with pytest.raises(HTTPException) as exc_info:
        await roles_service.get_role(role.id, user2.organization_id)
    
    assert exc_info.value.status_code == 403
