import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.schemas import ClosetItemCreate, ClosetItemOut, ClosetItemUpdate, SuccessResponse
from app.services.closet_service import ClosetService

router = APIRouter(prefix="/closet-items", tags=["Closet"])


@router.post("", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
async def create_closet_item(body: ClosetItemCreate, db: AsyncSession = Depends(get_db)):
    item = await ClosetService.create_item(db, body)
    return SuccessResponse(data=ClosetItemOut.model_validate(item))


@router.get("/{item_id}", response_model=SuccessResponse)
async def get_closet_item(item_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    item = await ClosetService.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Closet item not found")
    return SuccessResponse(data=ClosetItemOut.model_validate(item))


@router.patch("/{item_id}", response_model=SuccessResponse)
async def update_closet_item(item_id: uuid.UUID, body: ClosetItemUpdate, db: AsyncSession = Depends(get_db)):
    item = await ClosetService.update_item(db, item_id, body)
    if not item:
        raise HTTPException(status_code=404, detail="Closet item not found")
    return SuccessResponse(data=ClosetItemOut.model_validate(item))


@router.delete("/{item_id}", response_model=SuccessResponse)
async def delete_closet_item(item_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    deleted = await ClosetService.delete_item(db, item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Closet item not found")
    return SuccessResponse(data={"item_id": str(item_id), "deleted": True})
