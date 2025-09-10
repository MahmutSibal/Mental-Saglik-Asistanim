from fastapi import APIRouter, Depends
from ..schemas.mood import MoodTrendResponse, MoodPoint
from ..db.mongodb import messages_collection
from ..deps import get_current_user_id
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/weekly", response_model=MoodTrendResponse)
async def weekly(user_id: str = Depends(get_current_user_id)):
    return await _trend(user_id, days=7)

@router.get("/monthly", response_model=MoodTrendResponse)
async def monthly(user_id: str = Depends(get_current_user_id)):
    return await _trend(user_id, days=30)

async def _trend(user_id: str, days: int) -> MoodTrendResponse:
    col = messages_collection()
    since = datetime.utcnow() - timedelta(days=days)

    cursor = col.find({"user_id": user_id, "timestamp": {"$gte": since}}).sort("timestamp", 1)
    points = []
    distribution = {}
    async for doc in cursor:
        ts = doc["timestamp"].isoformat()
        label = doc.get("emotion", "unknown")
        points.append(MoodPoint(timestamp=ts, label=label))
        distribution[label] = distribution.get(label, 0) + 1
    return MoodTrendResponse(points=points, distribution=distribution)
