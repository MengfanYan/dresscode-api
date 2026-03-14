from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import EventRaw
from app.models.schemas import EventCreate


class EventService:
    @staticmethod
    async def create_event(db: AsyncSession, data: EventCreate) -> EventRaw:
        event = EventRaw(**data.model_dump())
        db.add(event)
        await db.commit()
        await db.refresh(event)
        return event
