from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from app.deps import get_current_user_id
from app.db.mongodb import checkins_collection
from app.schemas.checkin import CheckInCreate, CheckIn, CheckInSummary
from bson import ObjectId


router = APIRouter()


@router.post("/", response_model=CheckIn)
async def create_checkin(payload: CheckInCreate, user_id: str = Depends(get_current_user_id)):
    col = checkins_collection()
    doc = {
        "user_id": user_id,
        "score": int(payload.score),
        "note": (payload.note or "").strip() or None,
        "timestamp": datetime.utcnow(),
    }
    res = await col.insert_one(doc)
    return CheckIn(id=str(res.inserted_id), **doc)


@router.get("/today", response_model=CheckIn | None)
async def get_today_checkin(user_id: str = Depends(get_current_user_id)):
    col = checkins_collection()
    start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    doc = await col.find_one({"user_id": user_id, "timestamp": {"$gte": start}})
    if not doc:
        return None
    return CheckIn(id=str(doc["_id"]), user_id=doc["user_id"], score=doc["score"], note=doc.get("note"), timestamp=doc["timestamp"]) 


@router.get("/summary/{days}", response_model=CheckInSummary)
async def get_summary(days: int, user_id: str = Depends(get_current_user_id)):
    if days not in (7, 30):
        raise HTTPException(status_code=400, detail="days must be 7 or 30")
    col = checkins_collection()
    since = datetime.utcnow() - timedelta(days=days)
    cursor = col.find({"user_id": user_id, "timestamp": {"$gte": since}}).sort("timestamp", 1)
    items = [
        {
            "id": str(doc["_id"]),
            "score": doc["score"],
            "timestamp": doc["timestamp"],
        }
        async for doc in cursor
    ]
    if items:
        avg = sum(x["score"] for x in items) / len(items)
    else:
        avg = 0.0
    trend = [{"timestamp": x["timestamp"].isoformat(), "score": x["score"]} for x in items]
    return CheckInSummary(period=f"{days}d", avg_score=round(avg, 2), count=len(items), trend=trend)
