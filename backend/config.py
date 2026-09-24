import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]

ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(ENV_FILE)


# ============================================================
# DATABASE
# ============================================================

MYSQL_HOST = os.getenv(
    "MYSQL_HOST",
    "localhost"
)

MYSQL_PORT = int(
    os.getenv(
        "MYSQL_PORT",
        "3306"
    )
)

MYSQL_USER = os.getenv(
    "MYSQL_USER",
    "root"
)

MYSQL_PASSWORD = os.getenv(
    "MYSQL_PASSWORD",
    ""
)

MYSQL_DATABASE = os.getenv(
    "MYSQL_DATABASE",
    "ai_document_screening"
)


# ============================================================
# SERVER
# ============================================================

HOST = os.getenv(
    "HOST",
    "127.0.0.1"
)

PORT = int(
    os.getenv(
        "PORT",
        "8000"
    )
)


# ============================================================
# DIRECTORIES
# ============================================================

UPLOADS_DIR = Path(
    os.getenv(
        "UPLOADS_DIR",
        "/tmp/uploads" if os.getenv("VERCEL") else str(PROJECT_ROOT / "uploads")
    )
)

DOCUMENT_UPLOAD_DIR = (
    UPLOADS_DIR / "documents"
)

FACE_UPLOAD_DIR = (
    UPLOADS_DIR / "faces"
)


# ============================================================
# AI MODEL DIRECTORIES
# ============================================================

AI_MODELS_DIR = (
    PROJECT_ROOT / "ai_models"
)

DOCUMENT_CLASSIFIER_MODEL = (
    AI_MODELS_DIR
    / "document_classifier"
    / "model"
    / "document_classifier.keras"
)

DOCUMENT_CLASSIFIER_CLASSES = (
    AI_MODELS_DIR
    / "document_classifier"
    / "model"
    / "class_names.json"
)

FORGERY_MODEL = (
    AI_MODELS_DIR
    / "forgery_detector"
    / "model"
    / "forgery_detector.keras"
)

FORGERY_CLASSES = (
    AI_MODELS_DIR
    / "forgery_detector"
    / "model"
    / "class_names.json"
)

FACE_MODEL = (
    AI_MODELS_DIR
    / "face_verification"
    / "model"
    / "face_verification.keras"
)


# ============================================================
# SUPPORTED DOCUMENTS
# ============================================================

SUPPORTED_DOCUMENT_TYPES = {
    "pan": "PAN Card",
    "passport": "Passport",
    "voter_id": "Voter ID"
}


# ============================================================
# AI SETTINGS
# ============================================================

IMAGE_SIZE = (
    224,
    224
)

FORGERY_THRESHOLD = 0.50

FACE_SIMILARITY_THRESHOLD = 0.70


# ============================================================
# BLOCKCHAIN
# ============================================================

BLOCKCHAIN_ENABLED = (
    os.getenv(
        "BLOCKCHAIN_ENABLED",
        "false"
    ).lower()
    == "true"
)

BLOCKCHAIN_RPC_URL = os.getenv(
    "BLOCKCHAIN_RPC_URL",
    ""
)

BLOCKCHAIN_CONTRACT_ADDRESS = os.getenv(
    "BLOCKCHAIN_CONTRACT_ADDRESS",
    ""
)

BLOCKCHAIN_PRIVATE_KEY = os.getenv(
    "BLOCKCHAIN_PRIVATE_KEY",
    "" 
)


# ============================================================
# FILE SETTINGS
# ============================================================

MAX_UPLOAD_SIZE_MB = int(
    os.getenv(
        "MAX_UPLOAD_SIZE_MB",
        "10"
    )
)

ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp"
}


# ============================================================
# CREATE DIRECTORIES
# ============================================================

DOCUMENT_UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)

FACE_UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)