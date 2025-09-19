from datetime import datetime
from fastapi import APIRouter, Depends
from app.deps import get_current_user_id
from app.db.mongodb import feedback_collection
from app.schemas.feedback import FeedbackCreate, Feedback


router = APIRouter()


@router.post("/", response_model=Feedback)
async def create_feedback(payload: FeedbackCreate, user_id: str = Depends(get_current_user_id)):
    col = feedback_collection()
    doc = {
        "user_id": user_id,
        "target_type": payload.target_type,
        "target_id": payload.target_id,
        "vote": payload.vote,
        "emotion": payload.emotion,
        "timestamp": datetime.utcnow(),
    }
    res = await col.insert_one(doc)
    return Feedback(id=str(res.inserted_id), **doc)
