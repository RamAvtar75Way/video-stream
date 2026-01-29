from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

from app.routers import auth, videos, secure_stream


# BASE DIRECTORY (PROJECT ROOT)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
import logging

app = FastAPI(title="Video Streaming Backend")

# --------------------------------------------------
# Global Exception Handling
# --------------------------------------------------
logger = logging.getLogger(__name__)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global Exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error. Please contact support."}
    )

@app.exception_handler(SQLAlchemyError)
async def db_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"Database Error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Database operation failed."}
    )


# ROUTERS
app.include_router(auth.router)
app.include_router(videos.router)
app.include_router(secure_stream.router)

# SERVE HLS STREAM FILES
app.mount(
    "/stream",
    StaticFiles(directory=os.path.join(BASE_DIR, "media/hls")),
    name="stream"
)

# ROOT ENDPOINT
@app.get("/")
def root():
    return {"message": "Backend running 🚀"}
