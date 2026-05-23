# KhmerDoc AI

Khmer document understanding — OCR, field extraction, and layout detection for invoices, receipts, and forms.

## Stack

- **Backend** — FastAPI, Pydantic v2, file-based JSON storage
- **Frontend** — Next.js 16, React 19, TypeScript, Tailwind CSS 4

## Run

```bash
# Backend
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload

# Frontend
cd frontend
bun dev
```

Backend runs on `http://localhost:8000`, frontend on `http://localhost:3000`. API requests are proxied via Next.js rewrites.

## Pipeline

1. **Upload** — POST `/api/v1/documents/upload`
2. **OCR** — POST `/api/v1/documents/{id}/ocr`
3. **Extraction** — POST `/api/v1/documents/{id}/extract`
4. **Layout** — POST `/api/v1/documents/{id}/layout`

Layout detection currently uses a **mock detector** returning placeholder regions. A YOLOv8 model can be plugged in by replacing `MockLayoutDetector` with a real detector class that implements the same `detect(width, height)` interface.

## Storage

All data is stored under `storage/` as JSON files — no database required.

```
storage/
  uploads/           # original files
  ocr_outputs/       # OCR results
  extractions/       # extracted fields
  layouts/           # layout detection results
```