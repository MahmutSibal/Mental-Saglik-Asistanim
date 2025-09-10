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
from app.routers import messages as messages_router
from app.routers import me as me_router
from app.routers import profile as profile_router
from app.routers import vision as vision_router
from app.core.config import settings
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.core.limiter import limiter, RateLimitExceeded, rate_limit_handler

app = FastAPI(
    title="Mental Health Assistant API",
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
app.include_router(vision_router.router, prefix="/vision", tags=["vision"])  # image analysis

# Static uploads
UPLOAD_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'uploads'))
os.makedirs(UPLOAD_PATH, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_PATH), name="uploads")

# Static 3D models
MODELS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '3dmodel'))
if os.path.isdir(MODELS_PATH):
    app.mount("/models", StaticFiles(directory=MODELS_PATH), name="models")


@app.on_event("startup")
async def on_startup():
    await connect_to_mongo()


@app.on_event("shutdown")
async def on_shutdown():
    await close_mongo_connection()


@app.get("/health", tags=["meta"])
async def health():
    return {"status": "ok"}
