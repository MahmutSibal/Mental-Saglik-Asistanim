from fastapi import APIRouter, Depends
from ..schemas.suggestion import SuggestionResponse
from ..deps import get_current_user_id
from ..services.suggestions import fetch_suggestion_text, normalize

router = APIRouter()


@router.get("/{emotion}", response_model=SuggestionResponse)
async def get_suggestion(emotion: str, user_id: str = Depends(get_current_user_id)):
    emo = normalize(emotion)
    text = await fetch_suggestion_text(emo)
    return SuggestionResponse(emotion=emo, suggestion_text=text)
