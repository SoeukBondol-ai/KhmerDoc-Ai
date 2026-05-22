# KhmerDoc AI

Khmer document processing API — upload images, run OCR, extract structured fields.

## Pipeline

```
Upload Document → Kiri OCR → Extraction Service → Pydantic Validation → Saved JSON
```

1. Upload an image (receipt, invoice, etc.)
2. Run OCR to get raw text + line-level confidence
3. Run extraction to pull structured fields from OCR text
4. Results validated with Pydantic and saved as JSON

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/health` | Health check |
| `POST` | `/api/v1/documents/upload` | Upload a document (image/pdf) |
| `GET` | `/api/v1/documents` | List all documents |
| `GET` | `/api/v1/documents/{id}` | Get document detail with OCR + extraction |
| `POST` | `/api/v1/documents/{id}/ocr` | Run OCR on a document |
| `POST` | `/api/v1/documents/{id}/extract` | Run field extraction on OCR output |

## Extraction Output

```json
{
  "document_type": "receipt",
  "company_name": "ABC Shop",
  "phone": "012345678",
  "date": "2026-05-20",
  "invoice_number": "INV-001",
  "total_amount": "125000",
  "currency": "KHR",
  "confidence": 0.82
}
```

### Extracted Fields

| Field | How it's extracted |
|-------|--------------------|
| `document_type` | Fuzzy keyword match for "receipt", "invoice", "bill" |
| `company_name` | First non-Khmer text lines before structured data |
| `phone` | Regex for Cambodian phone patterns (0XX XXX XXX) |
| `date` | Regex for DD/MM/YYYY etc., with label detection ("Date:", "Date/TIME:") |
| `invoice_number` | Label detection ("Receipt ID:", "Invoice No:") |
| `total_amount` | "Grand Total" label, prefers Riel-denominated line |
| `currency` | Keyword match for "Riel"/"KHR"/"$"/"USD", falls back to amount magnitude |
| `confidence` | Weighted average of per-field confidence scores |

The extraction uses Levenshtein-based fuzzy matching to handle OCR typos (e.g., "Tootal" instead of "Total", "Ittem" instead of "Item").

## Project Structure

```
backend/
  app/
    api/
      deps.py                    # FastAPI dependency injection
      router.py                  # Top-level API router
      v1/routes/
        documents.py              # Document + OCR + extraction endpoints
        health.py                 # Health check
    core/
      config.py                  # Settings (pydantic-settings)
      lifespan.py                # App startup (creates dirs)
      exceptions.py              # HTTPException helpers
    schemas/
      document.py                # Document + OCR Pydantic models
      extraction.py               # Extraction Pydantic models
    services/
      document_store.py          # JSON-file-based document storage
      kiri_ocr_service.py        # Kiri OCR integration (Khmer OCR)
      ocr_pipeline.py           # OCR orchestration
      extraction_service.py      # Regex-based field extractors
      extraction_pipeline.py     # Extraction orchestration
    utils/
      files.py                   # File I/O helpers, upload logic
  storage/
    documents_index.json         # Document metadata index
    uploads/                     # Uploaded files
    ocr_outputs/                 # OCR result JSON files
    extractions/                  # Extraction result JSON files
```

## Setup

```bash
cd backend
uv sync
cp .env.sample .env   # add your env vars
uv run uvicorn app.main:app --reload
```

## Quick Test

```bash
# Upload a document
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -F "file=@receipt.jpg"

# Run OCR
curl -X POST http://localhost:8000/api/v1/documents/{doc_id}/ocr

# Run extraction
curl -X POST http://localhost:8000/api/v1/documents/{doc_id}/extract

# Get everything
curl http://localhost:8000/api/v1/documents/{doc_id}
```