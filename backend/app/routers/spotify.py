from fastapi import APIRouter, Query, HTTPException
import httpx

from app.schemas.spotify import SpotifyRecommendationsResponse, SpotifyTrack
from app.services.spotify import get_recommendations_for_emotion, SpotifyAuthError


router = APIRouter()


@router.get("/recommendations/{emotion}", response_model=SpotifyRecommendationsResponse)
async def recommendations(
	emotion: str,
	limit: int = Query(10, ge=1, le=50),
	market: str | None = Query(None),
	genre: str | None = Query(None, description="Override seed_genres e.g. pop"),
	seed_artists: str | None = Query(None, description="Comma-separated artist IDs"),
	seed_tracks: str | None = Query(None, description="Comma-separated track IDs"),
):
	try:
		tracks_raw = await get_recommendations_for_emotion(
			emotion,
			limit=limit,
			market=market,
			genre_override=genre,
			seed_artists=seed_artists,
			seed_tracks=seed_tracks,
		)
		tracks = [SpotifyTrack(**t) for t in tracks_raw]
		return SpotifyRecommendationsResponse(emotion=emotion, tracks=tracks)
	except SpotifyAuthError as e:
		raise HTTPException(status_code=400, detail=str(e))
	except HTTPException as e:
		# Pass through detailed HTTP errors from service (e.g., Spotify 400 with message)
		raise e
	except httpx.HTTPStatusError as e:
		code = e.response.status_code if e.response is not None else 502
		raise HTTPException(status_code=code, detail=f"Spotify API error: {e}")
	except Exception as e:
		raise HTTPException(status_code=502, detail=f"Spotify service error: {e}")

