# Mental Asistanım - Backend (FastAPI)

This FastAPI service provides authentication, emotion analysis via Hugging Face, mood trends, and suggestions stored in MongoDB.

## Features
- JWT-based register/login
- MongoDB via Motor
- /analyze uses HF model `j-hartmann/emotion-english-distilroberta-base`
- Stores messages with scores in `messages`
- Weekly/Monthly mood trends
- Suggestions endpoint using `suggestions` collection
- Spotify recommendations by emotion (client-credentials)
- CORS + basic rate limiting (SlowAPI)
- OpenAPI docs at /docs

## Setup
1. Create and configure `.env` from `.env.example`.
2. Install Python 3.10+ dependencies.

### Quickstart (Windows PowerShell)
```
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r backend\requirements.txt
```

Run API:
```
uvicorn app.main:app --reload --port 8000 --app-dir backend
```

### Seed suggestions data

Commands below assume you're running from the project root `c:\Users\-\Desktop\x` in Windows PowerShell.

1) Activate venv and install deps (if not already):
```
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r backend\requirements.txt
```

2) Ensure Python can import the backend package by setting PYTHONPATH to `backend` for this session:
```
$env:PYTHONPATH = "backend"
```

3) Seed suggestions (append to existing):
```
python backend\scripts\seed_suggestions.py seed
```

4) Replace existing suggestions instead of appending:
```
python backend\scripts\seed_suggestions.py seed --replace
```

5) Also include alias keys (e.g., mutlu -> joy, kaygı -> anxiety) pointing to canonical sets:
```
python backend\scripts\seed_suggestions.py seed --aliases
```

6) List a few items to verify:
```
python backend\scripts\seed_suggestions.py list --limit 10
```

7) Purge all suggestion documents (dangerous):
```
python backend\scripts\seed_suggestions.py purge
```

### Spotify integration
1. Create a Spotify app at https://developer.spotify.com/dashboard and get Client ID/Secret.
2. In `backend/.env`, set:
	- `SPOTIFY_CLIENT_ID=...`
	- `SPOTIFY_CLIENT_SECRET=...`
	- Optional: `SPOTIFY_MARKET=TR`
	- Optional: `SPOTIFY_REDIRECT_URI=http://127.0.0.1:8000/callback` (note: http, not htpp)
3. Endpoint: `GET /spotify/recommendations/{emotion}?limit=10`
	- Returns a list of tracks (name, artists, preview_url, external_url, image).
4. Frontend page `/suggest/:emotion` will render track suggestions if available.

Security note: Never commit real Spotify secrets to source control; rotate them if exposed.

## Collections
- users: {id, email, password, name, created_at}
- messages: {user_id, text, emotion, scores, timestamp}
- suggestions: {emotion, suggestion_text}

## Notes
- The first call to /analyze will download the HF model (internet required).
- For production, preload the model and set an adequate rate limit.
