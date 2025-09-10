from pydantic import BaseModel
from typing import List, Dict

class MessageOut(BaseModel):
    id: str
    text: str
    emotion: str
    scores: Dict[str, float]
    timestamp: str

class MessagesResponse(BaseModel):
    items: List[MessageOut]
