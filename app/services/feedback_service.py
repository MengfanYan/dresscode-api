import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import Feedback
from app.models.schemas import FeedbackCreate


class FeedbackService:
    @staticmethod
    async def create_feedback(db: AsyncSession, data: FeedbackCreate) -> Feedback:
        record = Feedback(**data.model_dump())
        db.add(record)
        await db.commit()
        await db.refresh(record)
        return record

    @staticmethod
    async def list_feedback(
        db: AsyncSession,
        user_id: uuid.UUID,
        *,
        signal: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Feedback]:
        stmt = select(Feedback).where(Feedback.user_id == user_id)
        if signal:
            stmt = stmt.where(Feedback.signal == signal)
        stmt = stmt.order_by(Feedback.created_at.desc()).limit(limit).offset(offset)
        result = await db.execute(stmt)
        return list(result.scalars().all())
