from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.schemas import FeedbackCreate, FeedbackOut, SuccessResponse
from app.services.feedback_service import FeedbackService

router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.post("", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
async def submit_feedback(body: FeedbackCreate, db: AsyncSession = Depends(get_db)):
    record = await FeedbackService.create_feedback(db, body)
    return SuccessResponse(data=FeedbackOut.model_validate(record))
