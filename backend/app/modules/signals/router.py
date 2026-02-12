"""
Router for candidate signals endpoints.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.models import User
from app.modules.auth.router import get_current_user
from app.modules.signals.service import SignalsService
from app.schemas.signal import SignalResponse


router = APIRouter()


@router.get("/candidate/{candidate_id}/role/{role_id}", response_model=SignalResponse)
async def get_signals(
    candidate_id: int,
    role_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SignalResponse:
    service = SignalsService(db)
    return await service.get_signals(candidate_id, role_id, current_user)
