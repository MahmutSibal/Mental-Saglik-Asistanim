import os
import sys
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from slowapi.middleware import SlowAPIMiddleware

# Allow running as script: add project root to sys.path so `import app.*` works
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from app.routers import auth, analyze, mood, suggest
from app.routers import spotify as spotify_router
from app.routers import messages as messages_router
from app.routers import me as me_router
from app.routers import profile as profile_router
from app.routers import checkin as checkin_router
from app.routers import feedback as feedback_router
from app.routers import crisis as crisis_router
from app.core.config import settings
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.core.limiter import limiter, RateLimitExceeded, rate_limit_handler

app = FastAPI(
    title="Mental Asistanım API",
    version="0.1.0",
    description="AI destekli ruh hali analizi ve öneri sistemi",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

origins = settings.CORS_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)
app.add_middleware(SlowAPIMiddleware)

# routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])  # register/login
app.include_router(me_router.router, prefix="/auth", tags=["auth"])  # /auth/me
app.include_router(analyze.router, prefix="/analyze", tags=["analyze"])  # emotion detection
app.include_router(mood.router, prefix="/mood", tags=["mood"])  # trends weekly/monthly
app.include_router(suggest.router, prefix="/suggest", tags=["suggest"])  # suggestions
app.include_router(messages_router.router, prefix="/messages", tags=["messages"])  # history
app.include_router(profile_router.router, tags=["profile"])  # /profile endpoints
app.include_router(spotify_router.router, prefix="/spotify", tags=["spotify"])  # spotify recommendations
app.include_router(checkin_router.router, prefix="/checkin", tags=["checkin"])  # daily check-ins
app.include_router(feedback_router.router, prefix="/feedback", tags=["feedback"])  # thumbs up/down
app.include_router(crisis_router.router, prefix="/crisis", tags=["crisis"])  # crisis resources

# Static uploads
UPLOAD_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'uploads'))
os.makedirs(UPLOAD_PATH, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_PATH), name="uploads")


@app.on_event("startup")
async def on_startup():
    await connect_to_mongo()


@app.on_event("shutdown")
async def on_shutdown():
    await close_mongo_connection()


@app.get("/health", tags=["meta"])
async def health():
    return {"status": "ok"}
