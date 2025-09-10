from pydantic import BaseModel
from typing import List, Dict

class MoodPoint(BaseModel):
    timestamp: str
    label: str

class MoodTrendResponse(BaseModel):
    points: List[MoodPoint]
    distribution: Dict[str, int]
