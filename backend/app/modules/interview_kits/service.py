"""
Service layer for interview kits operations.

Handles interview kit generation using AI and validation.
"""
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models import InterviewKit, Role, User
from app.modules.ai.client import AIClient
from app.modules.ai.parser import parse_interview_kit_response, LLMParseError
from app.modules.ai.validators import validate_interview_kit, LLMValidationError
from app.modules.interview_kits.repository import InterviewKitsRepository
from app.schemas.interview_kit import InterviewKitGenerateRequest


class InterviewKitsService:
    """Service for interview kits operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = InterviewKitsRepository(db)
        self.ai_client = AIClient()

    async def _get_role_or_404(self, role_id: int) -> Role:
        role = await self.repository.get_role_with_competencies(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found",
            )
        return role

    def _ensure_role_access(self, role: Role, user: User) -> None:
        if role.organization_id != user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Role does not belong to your organization",
            )

    async def generate_interview_kit(
        self,
        request: InterviewKitGenerateRequest,
        user: User,
    ) -> InterviewKit:
        """
        Generate an interview kit using AI and store it.
        """
        role = await self._get_role_or_404(request.role_id)
        self._ensure_role_access(role, user)

        competencies_payload = [
            {
                "id": comp.id,
                "name": comp.name,
                "description": comp.description,
                "weight": comp.weight,
            }
            for comp in role.competencies
        ]

        try:
            raw_response = await self.ai_client.generate_interview_kit(
                role_title=role.title,
                role_description=role.description,
                seniority_level=role.seniority_level,
                competencies=competencies_payload,
            )
            parsed = parse_interview_kit_response(raw_response)
            competency_ids = {comp.id for comp in role.competencies}
            validate_interview_kit(parsed, competency_ids)
        except (LLMParseError, LLMValidationError) as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(exc),
            )
        except Exception as exc:
            print("LLM invocation failed (interview kits):", repr(exc))
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="LLM invocation failed; please retry",
            )

        async with self.db.begin_nested():
            kit = await self.repository.create_interview_kit(
                role_id=role.id,
                llm_model=settings.openai_model if settings.openai_api_key else settings.ollama_model,
                questions=parsed["questions"],
            )

        return kit

    async def get_interview_kit(self, kit_id: int, user: User) -> InterviewKit:
        kit = await self.repository.get_interview_kit_by_id(kit_id)
        if not kit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview kit not found",
            )

        role = await self._get_role_or_404(kit.role_id)
        self._ensure_role_access(role, user)
        return kit

    async def list_interview_kits_for_role(self, role_id: int, user: User):
        role = await self._get_role_or_404(role_id)
        self._ensure_role_access(role, user)
        return await self.repository.list_interview_kits_by_role(role_id)
