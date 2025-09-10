from pydantic import BaseModel

class SuggestionResponse(BaseModel):
    emotion: str
    suggestion_text: str
