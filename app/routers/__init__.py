from fastapi import APIRouter
from .convert_router import router as convert_router
from .transcribe_router import router as transcribe_router
from .recordings_router import router as recordings_router
from .auth_router import router as auth_router


router = APIRouter()

router.include_router(convert_router, tags=["Convert"])
router.include_router(transcribe_router, tags=["Transcribe"])
router.include_router(recordings_router, tags=["recordings"])
router.include_router(auth_router, prefix="/auth", tags=["auth"])

