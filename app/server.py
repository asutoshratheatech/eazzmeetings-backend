"""
Main server configuration and startup logic.
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
# Exception Handling
from app.utils.exception_handler import global_exception_handler

from app.env_settings import env
from app.routers import router as main_router
from app.models.database import (
    UserCollection,
    UserSecretsCollection,
    IdentityCollection,
    IdentityEmbeddingCollection,
    RecordingCollection,
    MeetingCollection
)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    Lifecycle manager for the FastAPI app.
    Handles startup (DB connection, dir creation) and shutdown events.
    """
    # Init DB
    client = AsyncIOMotorClient(env.MONGODB_URL)
    await init_beanie(database=client.eazzmeetings, document_models=[
        UserCollection,
        UserSecretsCollection,
        IdentityCollection,
        IdentityEmbeddingCollection,
        RecordingCollection,
        MeetingCollection
    ])
    print("✅ Startup: Connected to Database")

    audio_dir = env.AUDIO_DIR_PATH or "recordings"

    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)
        print(f"✅ Startup: Created directory '{audio_dir}'")
    else:
        print(f"✅ Startup: Directory '{audio_dir}' exists")

    yield  # Application runs here

    # --- Shutdown Logic (Optional) ---
    print("🛑 Shutting down...")


app = FastAPI(
    title='eazzmeetings',
    version='0.0.1',
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.add_exception_handler(Exception, global_exception_handler)

# Include main router
app.include_router(main_router, prefix="/api")
# Iapp.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
# app.include_router(recordings_router, prefix="/api", tags=["Recordings"])
# app.include_router(mom_router, prefix="/api", tags=["MoM"])


# Upload Files Setup
UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploaded_files", StaticFiles(directory=UPLOAD_DIR), name="uploaded_files")

# Health Check
@app.get('/health')
def health_route():
    """
    Health check endpoint.
    """
    return {'status': 'ok'}

# Base Route
@app.get('/')
def base_route():
    """
    Root endpoint.
    """
    return {'message': 'Welcome to EazzMeetings'}

