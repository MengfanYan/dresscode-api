import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.schemas import (
    ExposureDetailOut,
    OutfitImageOut,
    OutfitSearchRequest,
    RecommendationRequest,
    RecommendationOut,
    SuccessResponse,
)
from app.services.recommendation_service import RecommendationService

router = APIRouter(tags=["Recommendations"])


@router.post("/recommendations/today", response_model=SuccessResponse)
async def generate_recommendation(body: RecommendationRequest, db: AsyncSession = Depends(get_db)):
    result = await RecommendationService.generate(db, body)
    return SuccessResponse(data=result)


@router.get("/recommendations/{request_id}", response_model=SuccessResponse)
async def get_exposure_detail(request_id: str, db: AsyncSession = Depends(get_db)):
    exposure = await RecommendationService.get_exposure(db, request_id)
    if not exposure:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return SuccessResponse(data=ExposureDetailOut.model_validate(exposure))


@router.post("/outfits/search", response_model=SuccessResponse)
async def search_outfits(body: OutfitSearchRequest, db: AsyncSession = Depends(get_db)):
    items = await RecommendationService.search_outfits(db, body)
    return SuccessResponse(data={"items": [OutfitImageOut.model_validate(i) for i in items]})
