import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.routes.api import router as api_router
from app.repositories.dictionary_repo import DictionaryRepository
from app.utils.exception_handlers import (
    global_exception_handler,
    http_exception_handler,
    validation_exception_handler
)

app = FastAPI(
    title="Wordle Solver API", 
    description="High-performance, modular backend for the Wordle Solver", 
    version="1.0.0"
)

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Global Exception Handlers
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# Include API Routes
app.include_router(api_router)

@app.on_event("startup")
def startup_event():
    """
    Initializes the application on startup.
    """
    DictionaryRepository.load()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
