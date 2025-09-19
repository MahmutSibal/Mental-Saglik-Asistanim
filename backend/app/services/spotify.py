from __future__ import annotations

import base64
import time
from typing import Any, Dict, List, Optional

import httpx
from fastapi import HTTPException

from app.core.config import settings


_token_cache: Dict[str, Any] = {"access_token": None, "expires_at": 0.0}
_genres_cache: Dict[str, Any] = {"seeds": None, "expires_at": 0.0}


class SpotifyAuthError(Exception):
	pass


def _b64(s: str) -> str:
	return base64.b64encode(s.encode()).decode()


async def _get_access_token() -> str:
	"""Get (and cache) a client-credentials access token."""
	now = time.time()
	if _token_cache.get("access_token") and now < _token_cache.get("expires_at", 0):
		return _token_cache["access_token"]

	client_id = settings.SPOTIFY_CLIENT_ID
	client_secret = settings.SPOTIFY_CLIENT_SECRET
	if not client_id or not client_secret:
		raise SpotifyAuthError("Spotify credentials missing. Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in .env")

	token_url = "https://accounts.spotify.com/api/token"
	auth_header = _b64(f"{client_id}:{client_secret}")

	try:
		async with httpx.AsyncClient(timeout=15.0) as client:
			resp = await client.post(
				token_url,
				data={"grant_type": "client_credentials"},
				headers={"Authorization": f"Basic {auth_header}", "Content-Type": "application/x-www-form-urlencoded"},
			)
			resp.raise_for_status()
	except httpx.HTTPStatusError as e:
		detail = "Spotify auth failed. Check SPOTIFY_CLIENT_ID/SECRET."
		# try to include upstream message
		try:
			err_json = e.response.json()
			if isinstance(err_json, dict):
				msg = err_json.get("error_description") or err_json.get("error")
				if msg:
					detail += f" ({msg})"
		except Exception:
			pass
		raise HTTPException(status_code=401, detail=detail) from e

	data = resp.json()
	access_token = data.get("access_token")
	if not access_token:
		raise HTTPException(status_code=401, detail="Spotify auth did not return access token.")
	expires_in = int(data.get("expires_in", 3600))
	_token_cache["access_token"] = access_token
	_token_cache["expires_at"] = time.time() + expires_in - 60  # refresh 1 min early
	return access_token


def _emotion_to_recommendation_params(emotion: str) -> Dict[str, Any]:
	emo = emotion.lower()
	# Turkish -> English normalization
	tr_map = {
		"mutlu": "joy",
		"mutluluk": "joy",
		"üzgün": "sadness",
		"uzgun": "sadness",
		"üzüntü": "sadness",
		"kızgın": "anger",
		"kizgin": "anger",
		"öfke": "anger",
		"korku": "fear",
		"iğrenme": "disgust",
		"igrenme": "disgust",
		"şaşkınlık": "surprise",
		"saskinlik": "surprise",
		"nötr": "neutral",
		"notr": "neutral",
	}
	emo = tr_map.get(emo, emo)
	# Basic mapping heuristics; tweak as desired
	mapping: Dict[str, Dict[str, Any]] = {
		"joy": {"target_valence": 0.9, "min_energy": 0.5, "seed_genres": "pop"},
		"sadness": {"target_valence": 0.2, "max_energy": 0.5, "seed_genres": "acoustic"},
		"anger": {"target_valence": 0.3, "target_energy": 0.8, "seed_genres": "rock"},
		"fear": {"target_valence": 0.3, "max_energy": 0.6, "seed_genres": "ambient"},
		"disgust": {"target_valence": 0.4, "seed_genres": "alt-rock"},
		"surprise": {"target_valence": 0.7, "seed_genres": "dance"},
		"neutral": {"target_valence": 0.5, "seed_genres": "chill"},
	}
	default = {"target_valence": 0.6, "seed_genres": "pop"}
	return mapping.get(emo, default)


def _emotion_to_search_query(emotion: str) -> str:
	emo = emotion.lower()
	tr_map = {
		"mutlu": "joy",
		"mutluluk": "joy",
		"üzgün": "sadness",
		"uzgun": "sadness",
		"üzüntü": "sadness",
		"kızgın": "anger",
		"kizgin": "anger",
		"öfke": "anger",
		"korku": "fear",
		"iğrenme": "disgust",
		"igrenme": "disgust",
		"şaşkınlık": "surprise",
		"saskinlik": "surprise",
		"nötr": "neutral",
		"notr": "neutral",
	}
	emo = tr_map.get(emo, emo)
	queries = {
		"joy": "happy upbeat",
		"sadness": "sad calm acoustic",
		"anger": "rock energetic",
		"fear": "ambient relaxing",
		"disgust": "melancholy alternative",
		"surprise": "energetic surprise",
		"neutral": "chill focus",
	}
	return queries.get(emo, "mood")


async def _search_tracks_fallback(token: str, emotion: str, limit: int = 10) -> List[Dict[str, Any]]:
	"""If recommendations are empty/unavailable, search top tracks by mood keywords."""
	q = _emotion_to_search_query(emotion)
	url = "https://api.spotify.com/v1/search"
	params = {"q": q, "type": "track", "limit": str(max(1, min(limit, 20)))}
	try:
		async with httpx.AsyncClient(timeout=15.0) as client:
			resp = await client.get(url, headers={"Authorization": f"Bearer {token}"}, params=params)
			resp.raise_for_status()
			data = resp.json() or {}
			items = (((data.get("tracks") or {}).get("items")) or [])
	except httpx.HTTPError:
		items = []
	tracks: List[Dict[str, Any]] = []
	for t in items:
		tracks.append(
			{
				"id": t.get("id"),
				"name": t.get("name"),
				"artists": ", ".join(a.get("name") for a in t.get("artists", []) if a.get("name")),
				"external_url": (t.get("external_urls", {}) or {}).get("spotify"),
				"preview_url": t.get("preview_url"),
				"album": (t.get("album", {}) or {}).get("name"),
				"image": next((img.get("url") for img in (t.get("album", {}) or {}).get("images", []) if img.get("url")), None),
			}
		)
	return tracks


async def get_recommendations_for_emotion(
	emotion: str,
	limit: int = 10,
	market: Optional[str] = None,
	genre_override: Optional[str] = None,
	seed_artists: Optional[str] = None,
	seed_tracks: Optional[str] = None,
) -> List[Dict[str, Any]]:
	token = await _get_access_token()
	params = _emotion_to_recommendation_params(emotion)
	q = {
		"limit": str(max(1, min(limit, 50))),
		"seed_genres": genre_override or params.get("seed_genres", "pop"),
	}
	if seed_artists:
		q["seed_artists"] = seed_artists
	if seed_tracks:
		q["seed_tracks"] = seed_tracks
	# include audio features if specified
	for key in [
		"target_acousticness",
		"target_danceability",
		"target_energy",
		"target_instrumentalness",
		"target_liveness",
		"target_loudness",
		"target_speechiness",
		"target_tempo",
		"target_valence",
		"min_energy",
		"max_energy",
		"min_tempo",
		"max_tempo",
	]:
		if key in params:
			q[key] = params[key]

	if market or settings.SPOTIFY_MARKET:
		q["market"] = (market or settings.SPOTIFY_MARKET)

	# Validate seed_genres against available seeds to avoid 400
	async def _get_available_genres() -> List[str]:
		now = time.time()
		if _genres_cache.get("seeds") and now < _genres_cache.get("expires_at", 0):
			return _genres_cache["seeds"]
		url = "https://api.spotify.com/v1/recommendations/available-genre-seeds"
		try:
			async with httpx.AsyncClient(timeout=15.0) as client:
				r = await client.get(url, headers={"Authorization": f"Bearer {token}"})
				r.raise_for_status()
				seeds = (r.json() or {}).get("genres", [])
				if not isinstance(seeds, list):
					seeds = []
				_genres_cache["seeds"] = seeds
				_genres_cache["expires_at"] = time.time() + 6 * 3600  # 6 hours
				return seeds
		except httpx.HTTPError:
			# If Spotify returns 404/5xx, skip validation and rely on safe defaults
			return []

	seeds = await _get_available_genres()
	if seeds and "seed_genres" in q:
		desired = q.get("seed_genres", "pop")
		# If desired seed not in seeds list, pick a common safe fallback
		if desired not in seeds:
			for fallback in ["pop", "rock", "dance", "chill", "acoustic"]:
				if fallback in seeds:
					q["seed_genres"] = fallback
					break

	url = "https://api.spotify.com/v1/recommendations"
	async def _request(params: Dict[str, Any]):
		async with httpx.AsyncClient(timeout=20.0) as client:
			r = await client.get(url, headers={"Authorization": f"Bearer {token}"}, params=params)
			r.raise_for_status()
			return r

	try:
		resp = await _request(q)
	except httpx.HTTPStatusError:
		# Fallback 1: only keep required seeds + limit (+market if present)
		fallback1 = {k: v for k, v in q.items() if k in ("seed_genres", "limit", "market")}
		try:
			resp = await _request(fallback1)
		except httpx.HTTPStatusError:
			# Fallback 2: drop market as well (some accounts/regions can be strict)
			fallback2 = {k: v for k, v in fallback1.items() if k != "market"}
			try:
				resp = await _request(fallback2)
			except httpx.HTTPStatusError:
				# Fallback 3: iterate common genres to try to get any result
				for g in ["pop", "rock", "dance", "chill", "acoustic"]:
					try:
						resp = await _request({"seed_genres": g, "limit": fallback2.get("limit", "10")})
						break
					except httpx.HTTPStatusError:
						resp = None
				if not resp:
					# Final fallback: search by keywords
					return await _search_tracks_fallback(token, emotion, limit)

	data = resp.json()

	tracks: List[Dict[str, Any]] = []
	for t in data.get("tracks", []):
		tracks.append(
			{
				"id": t.get("id"),
				"name": t.get("name"),
				"artists": ", ".join(a.get("name") for a in t.get("artists", []) if a.get("name")),
				"external_url": (t.get("external_urls", {}) or {}).get("spotify"),
				"preview_url": t.get("preview_url"),
				"album": (t.get("album", {}) or {}).get("name"),
				"image": next((img.get("url") for img in (t.get("album", {}) or {}).get("images", []) if img.get("url")), None),
			}
		)
	# If recommendations are empty, try search fallback before returning
	if not tracks:
		return await _search_tracks_fallback(token, emotion, limit)
	return tracks

