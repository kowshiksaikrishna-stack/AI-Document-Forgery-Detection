import uuid
from pathlib import Path

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    HTTPException
)

from backend.config import (
    DOCUMENT_UPLOAD_DIR,
    FACE_UPLOAD_DIR,
    ALLOWED_EXTENSIONS,
    MAX_UPLOAD_SIZE_MB
)


router = APIRouter()


def validate_extension(
    filename: str
):

    extension = (
        Path(filename)
        .suffix
        .lower()
    )

    if extension not in ALLOWED_EXTENSIONS:

        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file type. "
                "Use JPG, JPEG, PNG or WEBP."
            )
        )

    return extension


async def save_upload(
    upload: UploadFile,
    destination: Path
):

    extension = validate_extension(
        upload.filename or ""
    )

    content = await upload.read()

    max_bytes = (
        MAX_UPLOAD_SIZE_MB
        * 1024
        * 1024
    )

    if len(content) > max_bytes:

        raise HTTPException(
            status_code=413,
            detail=(
                f"File is larger than "
                f"{MAX_UPLOAD_SIZE_MB} MB."
            )
        )

    filename = (
        f"{uuid.uuid4().hex}"
        f"{extension}"
    )

    output_path = (
        destination / filename
    )

    output_path.write_bytes(
        content
    )

    return (
        filename,
        output_path
    )


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form("")
):

    filename, path = await save_upload(
        file,
        DOCUMENT_UPLOAD_DIR
    )

    return {
        "status": "success",
        "message": "Document uploaded successfully",
        "filename": filename,
        "document_type": document_type,
        "path": str(path)
    }


@router.post("/upload-face")
async def upload_face(
    file: UploadFile = File(...)
):

    filename, path = await save_upload(
        file,
        FACE_UPLOAD_DIR
    )

    return {
        "status": "success",
        "message": "Face image uploaded successfully",
        "filename": filename,
        "path": str(path)
    }