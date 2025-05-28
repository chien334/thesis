from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from typing import List
import os
import models
import schemas
import security
from database import get_db
import google.generativeai as genai
from PIL import Image
import io

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)

# Global variable to store the AI model
ai_model = None

def set_ai_model(model):
    global ai_model
    ai_model = model

@router.post("/message", response_model=schemas.ChatResponse)
async def chat_with_ai(
    message: schemas.ChatRequest,
    current_user: models.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    if not ai_model:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI model is not initialized"
        )
    
    try:
        # Generate response from Gemini
        response = ai_model.generate_content(message.message)
        
        # Save chat history
        chat_history = models.ChatHistory(
            user_id=current_user.id,
            message=message.message,
            response=response.text
        )
        db.add(chat_history)
        db.commit()
        db.refresh(chat_history)
        
        return schemas.ChatResponse(
            response=response.text,
            chat_history_id=chat_history.id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/image", response_model=schemas.ChatResponse)
async def chat_with_image(
    message: str,
    image: UploadFile = File(...),
    current_user: models.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    if not ai_model:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI model is not initialized"
        )
    
    try:
        # Read and process image
        image_data = await image.read()
        pil_image = Image.open(io.BytesIO(image_data))
        
        # Generate response from Gemini
        response = ai_model.generate_content([message, pil_image])
        
        # Save chat history
        chat_history = models.ChatHistory(
            user_id=current_user.id,
            message=message,
            response=response.text
        )
        db.add(chat_history)
        db.commit()
        db.refresh(chat_history)
        
        return schemas.ChatResponse(
            response=response.text,
            chat_history_id=chat_history.id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/history", response_model=schemas.ChatHistoryList)
async def get_chat_history(
    skip: int = 0,
    limit: int = 10,
    current_user: models.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get chat history for current user, excluding detection history"""
    total = db.query(models.ChatHistory).filter(
        models.ChatHistory.user_id == current_user.id,
        ~models.ChatHistory.message.like("Image detection:%")
    ).count()
    
    history = db.query(models.ChatHistory).filter(
        models.ChatHistory.user_id == current_user.id,
        ~models.ChatHistory.message.like("Image detection:%")
    ).order_by(models.ChatHistory.created_at.desc()).offset(skip).limit(limit).all()
    
    return {"items": history, "total": total}