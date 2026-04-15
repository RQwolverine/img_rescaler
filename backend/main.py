import os
import mimetypes
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response

from routers.process import router as process_router

app = FastAPI(
    title="IMG Rescaler API",
    description="A4 line-art image rescaling service",
    version="1.0.0",
)

# CORS: allow local dev frontend + production frontend URL
allowed_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:3000",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in allowed_origins],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

app.include_router(process_router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}


# Serve frontend static files if the dist directory exists
_dist = Path(__file__).parent / "dist"
if _dist.exists():
    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        file = _dist / full_path
        if file.exists() and file.is_file():
            mime, _ = mimetypes.guess_type(str(file))
            return FileResponse(file, media_type=mime or "application/octet-stream")
        return FileResponse(_dist / "index.html", media_type="text/html")
