from pathlib import Path
from typing import Optional
import uuid

from fastapi import APIRouter, UploadFile, File, HTTPException

from backend.config import (
    DOCUMENT_UPLOAD_DIR,
    ALLOWED_EXTENSIONS,
    MAX_UPLOAD_SIZE_MB,
)
from backend.services.ai_service import detect_forgery

router = APIRouter()


async def save_file(upload: UploadFile) -> Path:
    """Save one uploaded document and return its path."""
    filename = upload.filename or ""
    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported image format. Use JPG, JPEG, PNG or WEBP.",
        )

    content = await upload.read()
    max_bytes = MAX_UPLOAD_SIZE_MB * 1024 * 1024

    if not content:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    if len(content) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"Uploaded file is too large. Maximum is {MAX_UPLOAD_SIZE_MB} MB.",
        )

    DOCUMENT_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    output_path = DOCUMENT_UPLOAD_DIR / f"{uuid.uuid4().hex}{extension}"
    output_path.write_bytes(content)
    return output_path


@router.post("/verify")
async def verify_document(document: UploadFile = File(...)):
    """
    Simple verification endpoint.

    Upload one document and immediately receive the AI forgery result.
    No OCR, face verification, database, blockchain, or history is required.
    """
    document_path = await save_file(document)

    try:
        ai_result = detect_forgery(document_path)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Document analysis failed: {exc}",
        ) from exc

    fake_probability = float(ai_result.get("fake_probability", 0.0))
    genuine_probability = float(ai_result.get("genuine_probability", 0.0))

    genuine_score = genuine_probability

    if genuine_score >= 80.0:
        verification_status = "REAL"
    elif genuine_score < 50.0:
        verification_status = "FAKE"
    else:
        verification_status = "NEEDS REVIEW"

    return {
        "status": "success",
        "verification_status": verification_status,
        "result": verification_status,
        "score": round(genuine_score, 2),
        "fake_probability": round(fake_probability, 2),
        "genuine_probability": round(genuine_probability, 2),
        "forgery_status": ai_result.get("status"),
        "message": ai_result.get("message", "Analysis completed."),
    }


@router.post("/forgery")
async def forgery(document: UploadFile = File(...)):
    """Compatibility endpoint for direct forgery testing."""
    document_path = await save_file(document)

    try:
        result = detect_forgery(document_path)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Document analysis failed: {exc}",
        ) from exc

    return {"status": "success", **result}
