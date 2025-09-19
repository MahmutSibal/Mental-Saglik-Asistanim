from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, conint


class CheckInCreate(BaseModel):
    score: conint(ge=0, le=10)
    note: Optional[str] = None


class CheckIn(BaseModel):
    id: str
    user_id: str
    score: int
    note: Optional[str] = None
    timestamp: datetime


class CheckInSummary(BaseModel):
    period: str  # '7d' or '30d'
    avg_score: float
    count: int
    trend: List[dict]
