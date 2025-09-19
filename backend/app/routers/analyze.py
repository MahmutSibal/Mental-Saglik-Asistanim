from fastapi import APIRouter, Depends, Request
from ..schemas.analysis import AnalyzeRequest, AnalyzeResponse, AnalyzeResult
from ..services.nlp import analyze_text, top_label, keyword_emotion, detect_crisis, is_uncertain
from ..db.mongodb import messages_collection
from ..deps import get_current_user_id
from datetime import datetime
from ..core.limiter import limiter
from ..services.suggestions import fetch_suggestion_text

router = APIRouter()

@router.post("/", response_model=AnalyzeResponse)
@limiter.limit("20/minute")
async def analyze(request: Request, req: AnalyzeRequest, user_id: str = Depends(get_current_user_id)):
    scores = analyze_text(req.text)
    # crisis detection
    crisis_flag, crisis_reason = detect_crisis(req.text)
    # pick label with uncertainty handling
    label = keyword_emotion(req.text) or top_label(scores)
    if is_uncertain(scores):
        label = "uncertain"

    col = messages_collection()
    await col.insert_one({
        "user_id": user_id,
        "text": req.text,
        "emotion": label,
        "scores": scores,
        "crisis": {"flagged": crisis_flag, "reason": crisis_reason} if crisis_flag else None,
        "timestamp": datetime.utcnow(),
    })

    # Inline suggestion for chat reply UX
    suggestion_text = await fetch_suggestion_text(label)

    # Attach suggestion into response under result for backward compatibility
    result = AnalyzeResult(label=label, scores=scores)
    # Dynamically add attribute for suggestion (Pydantic will ignore unknown fields unless model updated)
    payload = {"result": result.model_dump(), "suggestion_text": suggestion_text, "crisis": {"flagged": crisis_flag, "reason": crisis_reason} if crisis_flag else {"flagged": False}}
    return payload
