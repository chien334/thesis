from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import models
import schemas
import security
from database import get_db

router = APIRouter(
    prefix="/history",
    tags=["history"],
)

@router.post("", response_model=schemas.ChatHistory)
async def create_chat_history(
    chat: schemas.ChatHistoryCreate,
    current_user: models.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    db_chat = models.ChatHistory(
        user_id=current_user.id,
        message=chat.message,
        response=chat.response,
        image_path=chat.image_path
    )
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat

@router.get("/", response_model=List[schemas.ChatHistory])
async def get_chat_history(
    skip: int = 0,
    limit: int = 10,
    current_user: models.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    history = db.query(models.ChatHistory)\
        .filter(models.ChatHistory.user_id == current_user.id)\
        .offset(skip)\
        .limit(limit)\
        .all()
    return history

@router.get("/admin", response_model=List[schemas.ChatHistory])
async def get_all_chat_history(
    skip: int = 0,
    limit: int = 10,
    current_user: models.User = Depends(security.get_current_admin_user),
    db: Session = Depends(get_db)
):
    history = db.query(models.ChatHistory)\
        .offset(skip)\
        .limit(limit)\
        .all()
    return history

@router.get("/{history_id}", response_model=schemas.ChatHistory)
async def get_chat_history_item(
    history_id: int,
    current_user: models.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    history_item = db.query(models.ChatHistory)\
        .filter(models.ChatHistory.id == history_id)\
        .first()
    
    if not history_item:
        raise HTTPException(status_code=404, detail="History item not found")
    
    if history_item.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return history_item

@router.delete("/{history_id}")
async def delete_chat_history(
    history_id: int,
    current_user: models.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    history_item = db.query(models.ChatHistory)\
        .filter(models.ChatHistory.id == history_id)\
        .first()
    
    if not history_item:
        raise HTTPException(status_code=404, detail="History item not found")
    
    if history_item.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db.delete(history_item)
    db.commit()
    
    return {"message": "History item deleted successfully"}
