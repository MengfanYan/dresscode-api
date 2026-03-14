import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import UserPreference
from app.models.schemas import UserPreferenceUpsert


class PreferenceService:
    @staticmethod
    async def get_preferences(db: AsyncSession, user_id: uuid.UUID) -> UserPreference | None:
        result = await db.execute(select(UserPreference).where(UserPreference.user_id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def upsert_preferences(db: AsyncSession, user_id: uuid.UUID, data: UserPreferenceUpsert) -> UserPreference:
        result = await db.execute(select(UserPreference).where(UserPreference.user_id == user_id))
        prefs = result.scalar_one_or_none()
        if prefs is None:
            prefs = UserPreference(user_id=user_id)
            db.add(prefs)
        updates = data.model_dump(exclude_none=True)
        for field, value in updates.items():
            setattr(prefs, field, value)
        await db.commit()
        await db.refresh(prefs)
        return prefs
