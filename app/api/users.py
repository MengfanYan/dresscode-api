import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.schemas import (
    ClosetItemListOut,
    ClosetItemOut,
    FeedbackListOut,
    FeedbackOut,
    PaginationMeta,
    RecommendationHistoryOut,
    SuccessResponse,
    UserCreate,
    UserOut,
    UserPreferenceOut,
    UserPreferenceUpsert,
    UserProfileOut,
    UserProfileUpdate,
)
from app.services.closet_service import ClosetService
from app.services.preference_service import PreferenceService
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
async def create_user(body: UserCreate, db: AsyncSession = Depends(get_db)):
    user = await UserService.create_user(db, body)
    return SuccessResponse(data=UserOut.model_validate(user))


@router.get("/{user_id}", response_model=SuccessResponse)
async def get_user(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    user = await UserService.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return SuccessResponse(data=UserOut.model_validate(user))


@router.patch("/{user_id}/profile", response_model=SuccessResponse)
async def update_user_profile(user_id: uuid.UUID, body: UserProfileUpdate, db: AsyncSession = Depends(get_db)):
    user = await UserService.update_profile(db, user_id, body)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return SuccessResponse(data=UserProfileOut.model_validate(user))


@router.get("/{user_id}/preferences", response_model=SuccessResponse)
async def get_preferences(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    prefs = await PreferenceService.get_preferences(db, user_id)
    if not prefs:
        raise HTTPException(status_code=404, detail="Preferences not found")
    return SuccessResponse(data=UserPreferenceOut.model_validate(prefs))


@router.patch("/{user_id}/preferences", response_model=SuccessResponse)
async def upsert_preferences(user_id: uuid.UUID, body: UserPreferenceUpsert, db: AsyncSession = Depends(get_db)):
    prefs = await PreferenceService.upsert_preferences(db, user_id, body)
    return SuccessResponse(data=UserPreferenceOut.model_validate(prefs))


@router.get("/{user_id}/closet-items", response_model=SuccessResponse)
async def list_closet_items(
    user_id: uuid.UUID,
    category: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    items = await ClosetService.list_items(db, user_id, category=category, limit=limit, offset=offset)
    return SuccessResponse(
        data=ClosetItemListOut(
            items=[ClosetItemOut.model_validate(i) for i in items],
            pagination=PaginationMeta(limit=limit, offset=offset),
        )
    )


@router.get("/{user_id}/recommendations/history", response_model=SuccessResponse)
async def recommendation_history(
    user_id: uuid.UUID,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    from app.services.recommendation_service import RecommendationService

    items = await RecommendationService.get_history(db, user_id, limit=limit, offset=offset)
    return SuccessResponse(
        data=RecommendationHistoryOut(
            items=items,
            pagination=PaginationMeta(limit=limit, offset=offset),
        )
    )


@router.get("/{user_id}/feedback", response_model=SuccessResponse)
async def list_feedback(
    user_id: uuid.UUID,
    signal: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    from app.services.feedback_service import FeedbackService

    items = await FeedbackService.list_feedback(db, user_id, signal=signal, limit=limit, offset=offset)
    return SuccessResponse(
        data=FeedbackListOut(
            items=[FeedbackOut.model_validate(i) for i in items],
            pagination=PaginationMeta(limit=limit, offset=offset),
        )
    )
