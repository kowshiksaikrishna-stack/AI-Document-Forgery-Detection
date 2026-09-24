import hashlib
from pathlib import Path
from typing import Optional

from backend.config import SUPPORTED_DOCUMENT_TYPES
from backend.database import execute_one, execute_query
from backend.security import hash_file
from backend.services.ai_service import (
    classify_document,
    detect_forgery
)
from backend.services.ocr_service import (
    extract_document_data
)
from backend.services.identity_service import (
    verify_identity
)
from backend.services.blockchain_service import (
    record_verification
)


# ============================================================
# DOCUMENT TYPE NORMALIZATION
# ============================================================

def normalize_document_type(
    document_type: Optional[str]
) -> Optional[str]:
    """
    Convert model/API document names into the standard
    project document names.

    Supported documents:
        PAN Card
        Passport
        Voter ID
    """

    if not document_type:
        return None

    value = str(
        document_type
    ).strip().lower()

    mapping = {
        "pan": "PAN Card",
        "pan_card": "PAN Card",
        "pan card": "PAN Card",

        "passport": "Passport",

        "voter": "Voter ID",
        "voter_id": "Voter ID",
        "voter id": "Voter ID"
    }

    return mapping.get(
        value,
        document_type
    )


# ============================================================
# DOCUMENT TYPE VALIDATION
# ============================================================

def is_supported_document_type(
    document_type: Optional[str]
) -> bool:

    if not document_type:
        return False

    normalized = normalize_document_type(
        document_type
    )

    return normalized in SUPPORTED_DOCUMENT_TYPES.values()


# ============================================================
# DOCUMENT HASH
# ============================================================

def calculate_document_hash(
    document_path
) -> str:
    """
    Calculate SHA-256 hash of the uploaded document.
    """

    return hash_file(
        document_path
    )


# ============================================================
# RISK CALCULATION
# ============================================================

def calculate_risk_score(
    document_confidence: float,
    ocr_confidence: float,
    genuine_probability: float,
    fake_probability: float,
    face_similarity: float,
    face_status: str
) -> float:
    """
    Calculate a prototype risk score from 0 to 100.

    Higher score = greater review risk.

    This is a prototype screening score and should not be
    treated as a definitive authenticity determination.
    """

    document_confidence = max(
        0.0,
        min(
            100.0,
            float(document_confidence)
        )
    )

    ocr_confidence = max(
        0.0,
        min(
            100.0,
            float(ocr_confidence)
        )
    )

    genuine_probability = max(
        0.0,
        min(
            100.0,
            float(genuine_probability)
        )
    )

    fake_probability = max(
        0.0,
        min(
            100.0,
            float(fake_probability)
        )
    )

    face_similarity = max(
        0.0,
        min(
            100.0,
            float(face_similarity)
        )
    )

    # Document classification risk.
    document_risk = (
        100.0 - document_confidence
    )

    # OCR risk.
    ocr_risk = (
        100.0 - ocr_confidence
    )

    # Forgery model risk.
    forgery_risk = fake_probability

    # Face risk is only included when a selfie was supplied
    # and face verification produced a meaningful result.
    face_available = face_status in [
        "MATCH",
        "NO_MATCH"
    ]

    if face_available:

        face_risk = (
            100.0 - face_similarity
        )

        risk = (
            document_risk * 0.25
            + ocr_risk * 0.15
            + forgery_risk * 0.40
            + face_risk * 0.20
        )

    else:

        # Redistribute the face weight when no face result
        # is available.
        risk = (
            document_risk * 0.30
            + ocr_risk * 0.20
            + forgery_risk * 0.50
        )

    return round(
        max(
            0.0,
            min(
                100.0,
                risk
            )
        ),
        2
    )


# ============================================================
# FINAL VERIFICATION RESULT
# ============================================================

def determine_result(
    document_confidence: float,
    ocr_status: str,
    genuine_probability: float,
    fake_probability: float,
    face_status: str
) -> str:
    """
    Determine the prototype screening result.

    Possible results:
        VERIFIED
        REJECTED
        NEEDS REVIEW

    The system intentionally uses NEEDS REVIEW for uncertain
    cases rather than treating an imperfect ML prediction as
    a definitive authenticity decision.
    """

    # Very low document classification confidence.
    if document_confidence < 60.0:
        return "NEEDS REVIEW"

    # Strong forgery signal.
    if fake_probability >= 70.0:
        return "REJECTED"

    # Face explicitly failed.
    if face_status == "NO_MATCH":
        return "NEEDS REVIEW"

    # Face detection failed.
    if face_status == "Face Not Detected":
        return "NEEDS REVIEW"

    # OCR failed.
    if ocr_status == "OCR Failed":
        return "NEEDS REVIEW"

    # Strong genuine signal with acceptable document/OCR data.
    if (
        genuine_probability >= 70.0
        and fake_probability < 50.0
        and ocr_status == "Verified"
        and face_status in [
            "MATCH",
            "Not Provided"
        ]
    ):
        return "VERIFIED"

    return "NEEDS REVIEW"


# ============================================================
# DATABASE INSERT
# ============================================================

def save_verification(
    user_id: Optional[int],
    document_type: str,
    document_hash: str,
    ocr_status: str,
    face_status: str,
    forgery_score: float,
    risk_score: float,
    result: str,
    blockchain_tx: Optional[str]
):
    """
    Save verification information to MySQL.

    Expected table:
        verifications
    """

    query = """
        INSERT INTO verifications (
            user_id,
            document_type,
            document_hash,
            ocr_status,
            face_status,
            forgery_score,
            risk_score,
            result,
            blockchain_tx
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
    """

    params = (
        user_id,
        document_type,
        document_hash,
        ocr_status,
        face_status,
        forgery_score,
        risk_score,
        result,
        blockchain_tx
    )

    return execute_query(
        query,
        params=params
    )


# ============================================================
# COMPLETE DOCUMENT VERIFICATION
# ============================================================

def verify_document(
    document_path,
    selfie_path=None,
    user_id: Optional[int] = None,
    requested_document_type: Optional[str] = None
):
    """
    Complete document verification pipeline.

    Pipeline:

        Uploaded document
              ↓
        AI classification
              ↓
        OCR extraction
              ↓
        Forgery detection
              ↓
        Optional face verification
              ↓
        SHA-256 document hash
              ↓
        Blockchain integrity record
              ↓
        MySQL verification history
              ↓
        Final result
    """

    document_path = Path(
        document_path
    )

    if not document_path.exists():

        raise FileNotFoundError(
            f"Document not found: {document_path}"
        )

    # --------------------------------------------------------
    # 1. DOCUMENT CLASSIFICATION
    # --------------------------------------------------------

    classification = classify_document(
        document_path
    )

    detected_type = normalize_document_type(
        classification.get(
            "document_type"
        )
    )

    document_confidence = float(
        classification.get(
            "confidence",
            0.0
        )
    )

    # --------------------------------------------------------
    # 2. REQUESTED TYPE CHECK
    # --------------------------------------------------------

    requested_type = normalize_document_type(
        requested_document_type
    )

    if requested_type and requested_type in SUPPORTED_DOCUMENT_TYPES.values():

        if detected_type != requested_type:

            # Keep the detected model result, but mark it
            # for review because the requested type differs.
            type_mismatch = True

        else:

            type_mismatch = False

    else:

        type_mismatch = False

    # --------------------------------------------------------
    # 3. SUPPORTED DOCUMENT CHECK
    # --------------------------------------------------------

    if not is_supported_document_type(
        detected_type
    ):

        document_hash = calculate_document_hash(
            document_path
        )

        return {
            "status": "success",
            "verification_id": None,
            "document_type": detected_type,
            "document_type_confidence": document_confidence,
            "ocr_status": "Needs Review",
            "face_status": "Not Provided",
            "face_similarity": 0.0,
            "forgery_score": 0.0,
            "genuine_probability": 0.0,
            "fake_probability": 0.0,
            "risk_score": 100.0,
            "result": "NEEDS REVIEW",
            "document_hash": document_hash,
            "blockchain_tx": None,
            "message": (
                "The uploaded document could not be "
                "classified as PAN Card, Passport or Voter ID."
            )
        }

    # --------------------------------------------------------
    # 4. OCR
    # --------------------------------------------------------

    ocr_result = extract_document_data(
        document_path,
        detected_type
    )

    ocr_status = ocr_result.get(
        "status",
        "Needs Review"
    )

    ocr_confidence = float(
        ocr_result.get(
            "confidence",
            0.0
        )
    )

    # --------------------------------------------------------
    # 5. FORGERY DETECTION
    # --------------------------------------------------------

    forgery_result = detect_forgery(
        document_path
    )

    forgery_status = forgery_result.get(
        "status",
        "NEEDS_REVIEW"
    )

    forgery_score = float(
        forgery_result.get(
            "forgery_score",
            0.0
        )
    )

    genuine_probability = float(
        forgery_result.get(
            "genuine_probability",
            0.0
        )
    )

    fake_probability = float(
        forgery_result.get(
            "fake_probability",
            0.0
        )
    )

    # --------------------------------------------------------
    # 6. FACE VERIFICATION
    # --------------------------------------------------------

    if selfie_path:

        face_result = verify_identity(
            document_image=document_path,
            selfie_image=selfie_path
        )

    else:

        face_result = {
            "status": "Not Provided",
            "similarity_score": 0.0,
            "cosine_similarity": 0.0,
            "threshold": 0.70,
            "message": (
                "Selfie was not provided."
            )
        }

    face_status = face_result.get(
        "status",
        "Not Provided"
    )

    face_similarity = float(
        face_result.get(
            "similarity_score",
            0.0
        )
    )

    # --------------------------------------------------------
    # 7. DOCUMENT HASH
    # --------------------------------------------------------

    document_hash = calculate_document_hash(
        document_path
    )

    # --------------------------------------------------------
    # 8. RISK SCORE
    # --------------------------------------------------------

    risk_score = calculate_risk_score(
        document_confidence=document_confidence,
        ocr_confidence=ocr_confidence,
        genuine_probability=genuine_probability,
        fake_probability=fake_probability,
        face_similarity=face_similarity,
        face_status=face_status
    )

    # --------------------------------------------------------
    # 9. FINAL RESULT
    # --------------------------------------------------------

    result = determine_result(
        document_confidence=document_confidence,
        ocr_status=ocr_status,
        genuine_probability=genuine_probability,
        fake_probability=fake_probability,
        face_status=face_status
    )

    # Requested type mismatch always requires review.
    if type_mismatch:

        result = "NEEDS REVIEW"

    # Explicit high-risk forgery result.
    if forgery_status == "HIGH_RISK":

        result = "REJECTED"

    # --------------------------------------------------------
    # 10. BLOCKCHAIN RECORD
    # --------------------------------------------------------

    blockchain_tx = None

    try:

        blockchain_result = record_verification(
            document_hash=document_hash,
            document_type=detected_type,
            result=result,
            risk_score=risk_score
        )

        if isinstance(
            blockchain_result,
            dict
        ):

            blockchain_tx = blockchain_result.get(
                "transaction_hash"
            )

            if blockchain_tx is None:

                blockchain_tx = blockchain_result.get(
                    "tx_hash"
                )

    except Exception:
        # Blockchain should not prevent the local verification
        # pipeline from returning its AI/OCR result.
        blockchain_tx = None

    # --------------------------------------------------------
    # 11. SAVE TO MYSQL
    # --------------------------------------------------------

    verification_id = None

    try:

        verification_id = save_verification(
            user_id=user_id,
            document_type=detected_type,
            document_hash=document_hash,
            ocr_status=ocr_status,
            face_status=face_status,
            forgery_score=forgery_score,
            risk_score=risk_score,
            result=result,
            blockchain_tx=blockchain_tx
        )

    except Exception as error:

        # Keep the verification result available even if the
        # database is temporarily unavailable.
        verification_id = None

        database_message = str(
            error
        )

    else:

        database_message = None

    # --------------------------------------------------------
    # 12. RESPONSE
    # --------------------------------------------------------

    message_parts = []

    message_parts.append(
        "Document verification completed."
    )

    if type_mismatch:

        message_parts.append(
            "Detected document type does not match "
            "the requested document type."
        )

    if forgery_status == "HIGH_RISK":

        message_parts.append(
            "The forgery detector produced a high-risk result."
        )

    if database_message:

        message_parts.append(
            "Verification result could not be saved to "
            "the database."
        )

    return {
        "status": "success",

        "verification_id": verification_id,

        "document_type": detected_type,

        "document_type_confidence": round(
            document_confidence,
            2
        ),

        "requested_document_type": requested_type,

        "type_mismatch": type_mismatch,

        "ocr_status": ocr_status,

        "ocr_confidence": round(
            ocr_confidence,
            2
        ),

        "ocr": ocr_result,

        "face_status": face_status,

        "face_similarity": round(
            face_similarity,
            2
        ),

        "face": face_result,

        "forgery_status": forgery_status,

        "forgery_score": round(
            forgery_score,
            2
        ),

        "genuine_probability": round(
            genuine_probability,
            2
        ),

        "fake_probability": round(
            fake_probability,
            2
        ),

        "risk_score": round(
            risk_score,
            2
        ),

        "result": result,

        "document_hash": document_hash,

        "blockchain_tx": blockchain_tx,

        "message": " ".join(
            message_parts
        )
    }


# ============================================================
# VERIFICATION HISTORY
# ============================================================

def get_history(
    user_id: int
):
    """
    Retrieve verification history for a user from MySQL.
    """

    query = """
        SELECT
            id,
            user_id,
            document_type,
            document_hash,
            ocr_status,
            face_status,
            forgery_score,
            risk_score,
            result,
            blockchain_tx,
            created_at
        FROM verifications
        WHERE user_id = %s
        ORDER BY created_at DESC, id DESC
    """

    return execute_query(
        query,
        params=(user_id,),
        fetch=True
    )


# ============================================================
# SINGLE VERIFICATION RECORD
# ============================================================

def get_verification(
    verification_id: int
):
    """
    Retrieve one verification record.
    """

    query = """
        SELECT
            id,
            user_id,
            document_type,
            document_hash,
            ocr_status,
            face_status,
            forgery_score,
            risk_score,
            result,
            blockchain_tx,
            created_at
        FROM verifications
        WHERE id = %s
    """

    return execute_one(
        query,
        params=(verification_id,)
    )