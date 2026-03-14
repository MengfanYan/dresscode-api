import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import ClosetItem
from app.models.schemas import ClosetItemCreate, ClosetItemUpdate


class ClosetService:
    @staticmethod
    async def create_item(db: AsyncSession, data: ClosetItemCreate) -> ClosetItem:
        item = ClosetItem(**data.model_dump())
        db.add(item)
        await db.commit()
        await db.refresh(item)
        return item

    @staticmethod
    async def get_item(db: AsyncSession, item_id: uuid.UUID) -> ClosetItem | None:
        result = await db.execute(select(ClosetItem).where(ClosetItem.item_id == item_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def list_items(
        db: AsyncSession,
        user_id: uuid.UUID,
        *,
        category: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[ClosetItem]:
        stmt = select(ClosetItem).where(ClosetItem.user_id == user_id)
        if category:
            stmt = stmt.where(ClosetItem.category == category)
        stmt = stmt.limit(limit).offset(offset)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def update_item(db: AsyncSession, item_id: uuid.UUID, data: ClosetItemUpdate) -> ClosetItem | None:
        result = await db.execute(select(ClosetItem).where(ClosetItem.item_id == item_id))
        item = result.scalar_one_or_none()
        if not item:
            return None
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(item, field, value)
        await db.commit()
        await db.refresh(item)
        return item

    @staticmethod
    async def delete_item(db: AsyncSession, item_id: uuid.UUID) -> bool:
        result = await db.execute(select(ClosetItem).where(ClosetItem.item_id == item_id))
        item = result.scalar_one_or_none()
        if not item:
            return False
        await db.delete(item)
        await db.commit()
        return True
