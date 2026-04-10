# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Backend
```bash
# Setup (one-time)
cd backend && python3.9 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Run dev server (from project root)
source backend/.venv/bin/activate
python -m uvicorn backend.main:app --port 8000 --reload
```

### Frontend
```bash
cd frontend
npm install        # one-time
npm run dev        # dev server at :5173, proxies /api → :8000
npm run build      # outputs to frontend/dist/
npm run lint
```

### Docker (full stack)
```bash
docker-compose up --build
```

## Architecture

Single-endpoint REST service: `POST /api/process` receives up to 9 images + JSON configs, returns base64-encoded rescaled images.

### Backend (`backend/`)
- `main.py` — FastAPI app, CORS via `ALLOWED_ORIGINS` env var (comma-separated), mounts router at `/api`
- `routers/process.py` — multipart handler: receives `files` + `configs` JSON array, fans out to pipeline
- `models/schemas.py` — Pydantic models: `ImageConfig`, `ProcessingResultItem`, `ProcessingResponse`
- `services/pipeline.py` — orchestrates the 4-step pipeline per image
- `services/ruler_detector.py` — column/row projection on grayscale strips → linear regression → `px_per_cm` + `ruler_origin`
- `services/content_detector.py` — connected component analysis to find top-art bounding box; excludes color regions (HSV saturation > 30)
- `services/scaler.py` — extracts ruler strips, scales content region, recomposes onto white A4 canvas

**Import style**: all imports are absolute (e.g. `from models.schemas import ...`), not relative. This is required for `uvicorn main:app` to work both locally and in Docker.

**Known image characteristics**: test images are 1079×1527 px, px/cm ≈ 51.35, `ruler_origin` ≈ (52, 35) px.

### Frontend (`frontend/src/`)
- `App.tsx` — 4-phase state machine: `upload → configure → processing → results`
- `api/client.ts` — Axios instance; reads `VITE_API_URL` env var (falls back to `''` for local proxy)
- `types/image.ts` — `ImageFile`, `ProcessingResult`, `ScaleMode`
- `components/upload/` — `DropZone` (drag-and-drop)
- `components/controls/` — `ImageCard` (per-file config), `ScaleModeSelect`
- `components/processing/` — `GenerateButton` with loading state
- `components/results/` — `DownloadCard` (renders base64 output, triggers download)

Animations use Framer Motion with `AnimatePresence` for phase transitions and staggered card entrances.

## Deployment

| Layer | Platform | Notes |
|-------|----------|-------|
| Backend | CloudBase 云托管 (Docker) | Public URL: `https://backend-244107-4-1258296249.sh.run.tcloudbase.com` |
| Frontend | CloudBase 静态托管 | `https://img-scaler-0gzyjy4c08d4f516-1258296249.tcloudbaseapp.com` |

**CORS**: set `ALLOWED_ORIGINS=https://img-scaler-0gzyjy4c08d4f516-1258296249.tcloudbaseapp.com` in CloudBase 云托管 env vars. After changing env vars, redeploy the backend service for changes to take effect.

**Frontend env**: `frontend/.env.production` sets `VITE_API_URL` to the CloudBase backend URL.

**Re-deploying frontend** (manual, from project root):
```bash
cd frontend && npm run build
tcb hosting deploy dist / -e img-scaler-0gzyjy4c08d4f516
```

**Re-deploying frontend** (auto): push changes under `frontend/**` to `main` branch — GitHub Actions runs `.github/workflows/deploy-frontend.yml`. Requires GitHub secrets: `TENCENT_SECRET_ID`, `TENCENT_SECRET_KEY`, `TCB_ENV_ID=img-scaler-0gzyjy4c08d4f516`.

**Re-deploying backend**: zip contents of `backend/` directory (not the directory itself), upload to CloudBase 云托管.

**Mobile**: frontend is responsive — panels stack vertically on mobile (< 768px), side-by-side on desktop (≥ 768px).
