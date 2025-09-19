from typing import List, Optional
from pydantic import BaseModel


class SpotifyTrack(BaseModel):
	id: str
	name: str
	artists: str
	external_url: Optional[str] = None
	preview_url: Optional[str] = None
	album: Optional[str] = None
	image: Optional[str] = None


class SpotifyRecommendationsResponse(BaseModel):
	emotion: str
	tracks: List[SpotifyTrack]
