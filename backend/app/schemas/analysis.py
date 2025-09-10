from pydantic import BaseModel, Field
from typing import Dict, List, Optional

class AnalyzeRequest(BaseModel):
    text: str = Field(min_length=1, description="User message to analyze")

class AnalyzeResult(BaseModel):
    label: str
    scores: Dict[str, float]  # probability per label

class AnalyzeResponse(BaseModel):
    result: AnalyzeResult
    suggestion_text: Optional[str] = None
