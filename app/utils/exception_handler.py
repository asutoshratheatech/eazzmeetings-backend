
import traceback
import logging
from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

async def global_exception_handler(request: Request, exc: Exception):
    """
    Centralized exception handler to catch all unhandled exceptions
    and return a structured JSON response with traceback.
    """
    logger.error(f"🔥 Global Exception Handler: {exc}")
    traceback.print_exc()
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc),
            "traceback": traceback.format_exc()
        }
    )
