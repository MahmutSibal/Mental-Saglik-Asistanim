from typing import List
from pydantic import BaseModel


class CrisisResource(BaseModel):
    title: str
    description: str
    phone: str | None = None
    url: str | None = None


class CrisisResponse(BaseModel):
    resources: List[CrisisResource]
