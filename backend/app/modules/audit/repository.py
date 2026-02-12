"""
Repository for audit logging.
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AuditLog


class AuditRepository:
    """Repository for audit log writes."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_log(
        self,
        entity_type: str,
        entity_id: int,
        action: str,
        actor_id: int,
        before_data: dict | None,
        after_data: dict | None,
    ) -> AuditLog:
        log = AuditLog(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            actor_id=actor_id,
            before_data=before_data,
            after_data=after_data,
        )
        self.db.add(log)
        await self.db.flush()
        await self.db.refresh(log)
        return log
