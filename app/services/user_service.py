import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import User
from app.models.schemas import UserCreate, UserProfileUpdate


class UserService:
    @staticmethod
    async def create_user(db: AsyncSession, data: UserCreate) -> User:
        user = User(
            email=data.email,
            username=data.username,
            profile=data.profile,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def get_user(db: AsyncSession, user_id: uuid.UUID) -> User | None:
        result = await db.execute(select(User).where(User.user_id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def update_profile(db: AsyncSession, user_id: uuid.UUID, data: UserProfileUpdate) -> User | None:
        result = await db.execute(select(User).where(User.user_id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return None
        existing = user.profile or {}
        updates = data.model_dump(exclude_none=True)
        user.profile = {**existing, **updates}
        await db.commit()
        await db.refresh(user)
        return user
