from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
import models
import schemas
import security
from database import get_db
from detection_utils import get_detector
import os
from datetime import datetime

router = APIRouter(
    prefix="/detect",
    tags=["detection"]
)

@router.post("/image", response_model=schemas.DetectionResponse)
async def detect_image(
    image: UploadFile = File(...),
    current_user: models.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    detector = get_detector()
    if not detector:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Image detection service is not available"
        )
    
    try:
        # Read image file
        image_data = await image.read()
        
        # Perform detection
        results = detector.detect(image_data)
        
        # Save detection history
        detection_history = models.ChatHistory(
            user_id=current_user.id,
            message="Image detection request",
            response=str(results),
            image_path=image.filename
        )
        db.add(detection_history)
        db.commit()
        db.refresh(detection_history)
        
        return schemas.DetectionResponse(
            results=results,
            detection_history_id=detection_history.id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/history", response_model=schemas.ChatHistoryList)
async def get_detection_history(
    skip: int = 0,
    limit: int = 10,
    current_user: models.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get detection history for current user"""
    total = db.query(models.ChatHistory).filter(
        models.ChatHistory.user_id == current_user.id,
        models.ChatHistory.message.like("Image detection:%")
    ).count()
    
    history = db.query(models.ChatHistory).filter(
        models.ChatHistory.user_id == current_user.id,
        models.ChatHistory.message.like("Image detection:%")
    ).order_by(models.ChatHistory.created_at.desc()).offset(skip).limit(limit).all()
    
    return {"items": history, "total": total}