from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# ============================================================
# AUTHENTICATION MODELS
# ============================================================

class RegisterRequest(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    email: EmailStr

    password: str = Field(
        ...,
        min_length=6,
        max_length=100
    )


class LoginRequest(BaseModel):
    email: EmailStr

    password: str = Field(
        ...,
        min_length=6,
        max_length=100
    )


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr


class LoginResponse(BaseModel):
    status: str
    message: str
    user: UserResponse


# ============================================================
# SUPPORTED DOCUMENT TYPES
# ============================================================

SUPPORTED_DOCUMENT_TYPES = [
    "PAN Card",
    "Passport",
    "Voter ID"
]


# ============================================================
# DOCUMENT UPLOAD
# ============================================================

class DocumentUploadResponse(BaseModel):
    status: str
    message: str
    filename: str
    document_type: Optional[str] = None
    path: Optional[str] = None


# ============================================================
# OCR RESULT
# ============================================================

class OCRResult(BaseModel):
    document_type: Optional[str] = None

    name: Optional[str] = None

    document_number: Optional[str] = None

    date_of_birth: Optional[str] = None

    gender: Optional[str] = None

    address: Optional[str] = None

    raw_text: Optional[str] = None

    confidence: float = 0.0

    status: str = "Needs Review"


# ============================================================
# FACE VERIFICATION
# ============================================================

class FaceVerificationResult(BaseModel):
    status: str

    similarity_score: float = 0.0

    message: Optional[str] = None


# ============================================================
# FORGERY DETECTION
# ============================================================

class ForgeryResult(BaseModel):
    status: str

    forgery_score: float = 0.0

    genuine_probability: float = 0.0

    fake_probability: float = 0.0

    message: Optional[str] = None


# ============================================================
# COMPLETE VERIFICATION RESULT
# ============================================================

class VerificationResult(BaseModel):
    verification_id: Optional[int] = None

    document_type: str

    document_type_confidence: float = 0.0

    ocr_status: str = "Needs Review"

    face_status: str = "Not Provided"

    face_similarity: float = 0.0

    forgery_score: float = 0.0

    genuine_probability: float = 0.0

    fake_probability: float = 0.0

    risk_score: float = 100.0

    result: str = "NEEDS REVIEW"

    document_hash: Optional[str] = None

    blockchain_tx: Optional[str] = None

    message: Optional[str] = None


# ============================================================
# VERIFICATION HISTORY
# ============================================================

class VerificationHistory(BaseModel):
    id: int

    user_id: int

    document_type: str

    document_hash: str

    ocr_status: Optional[str] = None

    face_status: Optional[str] = None

    forgery_score: Optional[float] = None

    risk_score: Optional[float] = None

    result: Optional[str] = None

    blockchain_tx: Optional[str] = None

    created_at: Optional[str] = None