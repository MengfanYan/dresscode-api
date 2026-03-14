from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.schemas import EventCreate, EventOut, SuccessResponse
from app.services.event_service import EventService

router = APIRouter(prefix="/events", tags=["Events"])


@router.post("", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
async def track_event(body: EventCreate, db: AsyncSession = Depends(get_db)):
    event = await EventService.create_event(db, body)
    return SuccessResponse(data=EventOut.model_validate(event))
