from fastapi import APIRouter, Depends, Query
from ..schemas.message import MessagesResponse, MessageOut
from ..db.mongodb import messages_collection
from ..deps import get_current_user_id

router = APIRouter()

@router.get("/", response_model=MessagesResponse)
async def list_messages(user_id: str = Depends(get_current_user_id), limit: int = Query(50, le=200)):
    col = messages_collection()
    cursor = col.find({"user_id": user_id}).sort("timestamp", -1).limit(limit)
    items = []
    async for doc in cursor:
        items.append(MessageOut(
            id=str(doc.get("_id")),
            text=doc.get("text", ""),
            emotion=doc.get("emotion", "unknown"),
            scores=doc.get("scores", {}),
            timestamp=doc.get("timestamp").isoformat() if doc.get("timestamp") else "",
        ))
    return MessagesResponse(items=items)
