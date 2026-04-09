import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
