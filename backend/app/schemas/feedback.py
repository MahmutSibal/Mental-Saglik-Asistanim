from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel


class FeedbackCreate(BaseModel):
    target_type: Literal["suggestion", "track"]
    target_id: str  # suggestion key or track id
    vote: Literal["up", "down"]
    emotion: Optional[str] = None


class Feedback(BaseModel):
    id: str
    user_id: str
    target_type: str
    target_id: str
    vote: str
    emotion: Optional[str] = None
    timestamp: datetime
