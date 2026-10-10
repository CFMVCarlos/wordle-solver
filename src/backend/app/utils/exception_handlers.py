from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import sys
import traceback

async def global_exception_handler(request: Request, exc: Exception):
    """
    Catches all unhandled exceptions globally and formats them to the required standard.
    Never exposes stack traces to the client.
    """
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": "An internal server error occurred.", "code": 500}
    )

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Formats standard HTTPExceptions.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "message": str(exc.detail), "code": exc.status_code}
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Formats Pydantic validation errors.
    """
    return JSONResponse(
        status_code=400,
        content={"status": "error", "message": "Invalid request payload.", "code": 400}
    )
