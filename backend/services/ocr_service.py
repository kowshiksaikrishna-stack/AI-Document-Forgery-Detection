from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Dict, Optional, Tuple

import cv2
import numpy as np
from PIL import Image, ImageOps, ImageFilter

try:
    import pytesseract
    from pytesseract import Output
    PYTESSERACT_AVAILABLE = True
except ImportError:
    pytesseract = None
    Output = None
    PYTESSERACT_AVAILABLE = False


# ============================================================
# TESSERACT CONFIGURATION
# ============================================================

def configure_tesseract() -> Optional[str]:
    """
    Finds the Tesseract executable on Windows.

    Priority:
    1. TESSERACT_CMD from .env/environment
    2. Common Windows installation paths
    3. tesseract.exe available in PATH
    """

    if not PYTESSERACT_AVAILABLE:
        return None

    configured = os.getenv("TESSERACT_CMD", "").strip()

    possible_paths = []

    if configured:
        possible_paths.append(configured)

    possible_paths.extend([
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.expandvars(
            r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe"
        ),
        os.path.expandvars(
            r"%LOCALAPPDATA%\Tesseract-OCR\tesseract.exe"
        ),
    ])

    for path in possible_paths:
        if path and Path(path).exists():
            try:
                pytesseract.pytesseract.tesseract_cmd = path
                return path
            except Exception:
                pass

    # Try PATH
    try:
        version = pytesseract.get_tesseract_version()
        if version:
            return "PATH"
    except Exception:
        pass

    return None


TESSERACT_PATH = configure_tesseract()


# ============================================================
# DOCUMENT TYPE NORMALIZATION
# ============================================================

DOCUMENT_TYPE_ALIASES = {
    "pan": "pan",
    "pan card": "pan",
    "pancard": "pan",

    "passport": "passport",

    "voter_id": "voter_id",
    "voter id": "voter_id",
    "voterid": "voter_id",
    "election id": "voter_id",
}


def normalize_document_type(document_type: Optional[str]) -> str:
    if not document_type:
        return ""

    value = str(document_type).strip().lower()
    value = re.sub(r"\s+", " ", value)

    return DOCUMENT_TYPE_ALIASES.get(value, value)


# ============================================================
# IMAGE LOADING
# ============================================================

def load_image(image_path) -> Image.Image:
    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError(f"OCR image not found: {path}")

    image = Image.open(path)

    # Convert to RGB
    image = image.convert("RGB")

    return image


# ============================================================
# IMAGE PREPROCESSING
# ============================================================

def preprocess_image(image: Image.Image) -> Image.Image:
    """
    Prepares an image for OCR.

    Steps:
    - RGB -> grayscale
    - contrast enhancement
    - upscale
    - light sharpening
    """

    image = image.convert("RGB")

    width, height = image.size

    # Upscale small documents.
    if width < 1400:
        scale = 1400 / max(width, 1)
        new_width = int(width * scale)
        new_height = int(height * scale)

        image = image.resize(
            (new_width, new_height),
            Image.Resampling.LANCZOS
        )

    gray = ImageOps.grayscale(image)

    # Improve contrast.
    gray = ImageOps.autocontrast(gray)

    # Slight sharpening.
    gray = gray.filter(ImageFilter.SHARPEN)

    return gray


def preprocess_cv(image_path) -> np.ndarray:
    """
    OpenCV preprocessing used as a second OCR attempt.
    """

    image = cv2.imread(str(image_path))

    if image is None:
        raise FileNotFoundError(
            f"Unable to read OCR image: {image_path}"
        )

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Upscale.
    height, width = gray.shape[:2]

    if width < 1400:
        scale = 1400 / max(width, 1)

        gray = cv2.resize(
            gray,
            (
                int(width * scale),
                int(height * scale)
            ),
            interpolation=cv2.INTER_CUBIC
        )

    # Remove noise.
    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    # Adaptive threshold.
    threshold = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11
    )

    return threshold


# ============================================================
# OCR ENGINE CHECK
# ============================================================

def get_ocr_status() -> Dict:
    """
    Returns diagnostic information about OCR installation.
    """

    result = {
        "pytesseract_installed": PYTESSERACT_AVAILABLE,
        "tesseract_available": False,
        "tesseract_path": TESSERACT_PATH,
        "version": None,
        "message": ""
    }

    if not PYTESSERACT_AVAILABLE:
        result["message"] = (
            "pytesseract is not installed. "
            "Run: pip install pytesseract"
        )
        return result

    path = configure_tesseract()

    if path is None:
        result["message"] = (
            "Tesseract OCR executable was not found. "
            "Install Tesseract OCR for Windows or set TESSERACT_CMD."
        )
        return result

    try:
        version = pytesseract.get_tesseract_version()

        result["tesseract_available"] = True
        result["version"] = str(version)
        result["tesseract_path"] = (
            pytesseract.pytesseract.tesseract_cmd
        )
        result["message"] = "Tesseract OCR is ready."

    except Exception as exc:
        result["message"] = f"Tesseract check failed: {exc}"

    return result


# ============================================================
# RAW TEXT EXTRACTION
# ============================================================

def extract_text(
    image_path,
    document_type: Optional[str] = None
) -> str:
    """
    Extract text using multiple OCR passes.
    """

    if not PYTESSERACT_AVAILABLE:
        return ""

    configure_tesseract()

    if not TESSERACT_PATH:
        # Re-check in case environment changed.
        if configure_tesseract() is None:
            return ""

    path = Path(image_path)

    if not path.exists():
        return ""

    document_type = normalize_document_type(document_type)

    texts = []

    try:
        image = load_image(path)
        processed = preprocess_image(image)

        # ----------------------------------------------------
        # Pass 1: general document OCR
        # ----------------------------------------------------

        text1 = pytesseract.image_to_string(
            processed,
            config="--oem 3 --psm 6"
        )

        if text1:
            texts.append(text1)

        # ----------------------------------------------------
        # Pass 2: sparse text OCR
        # ----------------------------------------------------

        text2 = pytesseract.image_to_string(
            processed,
            config="--oem 3 --psm 11"
        )

        if text2:
            texts.append(text2)

    except Exception:
        pass

    # --------------------------------------------------------
    # Pass 3: OpenCV threshold image
    # --------------------------------------------------------

    try:
        threshold = preprocess_cv(path)

        text3 = pytesseract.image_to_string(
            threshold,
            config="--oem 3 --psm 6"
        )

        if text3:
            texts.append(text3)

    except Exception:
        pass

    # --------------------------------------------------------
    # Combine OCR results
    # --------------------------------------------------------

    combined = "\n".join(texts)

    # Clean repeated blank lines.
    combined = re.sub(
        r"\n\s*\n\s*\n+",
        "\n\n",
        combined
    )

    return combined.strip()


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_value(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None

    value = str(value)

    value = value.replace("\x00", " ")

    value = re.sub(
        r"[ \t]+",
        " ",
        value
    )

    value = re.sub(
        r"\n+",
        "\n",
        value
    )

    value = value.strip()

    return value if value else None


def clean_ocr_text(text: str) -> str:
    if not text:
        return ""

    text = text.replace("\x00", " ")

    lines = []

    for line in text.splitlines():
        line = re.sub(r"[ \t]+", " ", line).strip()

        if line:
            lines.append(line)

    return "\n".join(lines)


# ============================================================
# REGEX HELPERS
# ============================================================

def find_first(
    text: str,
    patterns
) -> Optional[str]:

    if not text:
        return None

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE | re.MULTILINE
        )

        if match:
            try:
                value = match.group(1)
            except IndexError:
                value = match.group(0)

            value = clean_value(value)

            if value:
                return value

    return None


# ============================================================
# NAME EXTRACTION
# ============================================================

def extract_name(
    text: str,
    document_type: Optional[str] = None
) -> Optional[str]:

    document_type = normalize_document_type(document_type)

    patterns = [
        r"(?:name\s*[:\-]\s*)([A-Z][A-Z .'-]{2,80})",
        r"(?:full\s*name\s*[:\-]\s*)([A-Z][A-Z .'-]{2,80})",
        r"(?:surname\s*[:\-]\s*)([A-Z][A-Z .'-]{2,80})",
        r"(?:given\s*name\s*[:\-]\s*)([A-Z][A-Z .'-]{2,80})",
    ]

    value = find_first(text, patterns)

    if value:
        value = re.sub(
            r"\s{2,}",
            " ",
            value
        ).strip()

        return value

    # Fallback:
    # Search lines containing NAME.
    for line in text.splitlines():

        clean = line.strip()

        if not clean:
            continue

        upper = clean.upper()

        if "NAME" in upper:

            parts = re.split(
                r"NAME\s*[:\-]?",
                clean,
                flags=re.IGNORECASE
            )

            if len(parts) > 1:

                candidate = clean_value(parts[-1])

                if candidate and len(candidate) >= 2:

                    candidate = re.sub(
                        r"[^A-Za-z .'-]",
                        "",
                        candidate
                    ).strip()

                    if candidate:
                        return candidate

    return None


# ============================================================
# DATE OF BIRTH
# ============================================================

def extract_date_of_birth(text: str) -> Optional[str]:

    patterns = [
        r"(?:date\s*of\s*birth|dob|birth\s*date)"
        r"\s*[:\-]?\s*"
        r"(\d{1,2}[\/\-.]\d{1,2}[\/\-.]\d{2,4})",

        r"(?:date\s*of\s*birth|dob|birth)"
        r"\s*[:\-]?\s*"
        r"(\d{1,2}\s+[A-Za-z]{3,9}\s+\d{2,4})",

        r"(\d{1,2}[\/\-.]\d{1,2}[\/\-.]\d{4})",
    ]

    return find_first(text, patterns)


# ============================================================
# GENDER
# ============================================================

def extract_gender(text: str) -> Optional[str]:

    patterns = [
        r"(?:gender|sex)\s*[:\-]?\s*(MALE|FEMALE|M|F)",
    ]

    value = find_first(text, patterns)

    if not value:
        return None

    value_upper = value.upper()

    if value_upper == "M":
        return "Male"

    if value_upper == "F":
        return "Female"

    if value_upper in {"MALE", "FEMALE"}:
        return value_upper.title()

    return value


# ============================================================
# ADDRESS
# ============================================================

def extract_address(text: str) -> Optional[str]:

    patterns = [
        r"(?:address)\s*[:\-]\s*(.+)",
        r"(?:residential\s*address)\s*[:\-]\s*(.+)",
        r"(?:permanent\s*address)\s*[:\-]\s*(.+)",
    ]

    value = find_first(text, patterns)

    if value:
        return value

    return None


# ============================================================
# PAN NUMBER
# ============================================================

def extract_pan_number(text: str) -> Optional[str]:

    # Standard PAN structure:
    # ABCDE1234F

    pattern = r"\b([A-Z]{5}[0-9]{4}[A-Z])\b"

    match = re.search(
        pattern,
        text.upper()
    )

    if match:
        return match.group(1)

    # OCR can introduce spaces.
    compact = re.sub(
        r"[^A-Z0-9]",
        "",
        text.upper()
    )

    match = re.search(
        r"([A-Z]{5}[0-9]{4}[A-Z])",
        compact
    )

    if match:
        return match.group(1)

    return None


# ============================================================
# PASSPORT NUMBER
# ============================================================

def extract_passport_number(text: str) -> Optional[str]:

    patterns = [
        r"(?:passport\s*(?:no|number)?|document\s*no)"
        r"\s*[:\-]?\s*([A-Z0-9]{6,12})",

        r"\b([A-Z][0-9]{7})\b",
    ]

    return find_first(text, patterns)


# ============================================================
# VOTER ID
# ============================================================

def extract_voter_id_number(text: str) -> Optional[str]:

    patterns = [
        r"(?:epic\s*(?:no|number)?|voter\s*(?:id|no|number))"
        r"\s*[:\-]?\s*([A-Z]{2,5}[0-9]{5,12})",

        r"\b([A-Z]{3}[0-9]{7})\b",
    ]

    return find_first(text, patterns)


# ============================================================
# DOCUMENT NUMBER
# ============================================================

def extract_document_number(
    text: str,
    document_type: Optional[str]
) -> Optional[str]:

    document_type = normalize_document_type(document_type)

    if document_type == "pan":
        return extract_pan_number(text)

    if document_type == "passport":
        return extract_passport_number(text)

    if document_type == "voter_id":
        return extract_voter_id_number(text)

    # Generic fallback.
    patterns = [
        r"(?:document\s*(?:no|number))\s*[:\-]?\s*([A-Z0-9\-]{5,20})",
        r"(?:id\s*(?:no|number))\s*[:\-]?\s*([A-Z0-9\-]{5,20})",
    ]

    return find_first(text, patterns)


# ============================================================
# FIELD EXTRACTION
# ============================================================

def extract_fields(
    text: str,
    document_type: Optional[str] = None
) -> Dict:

    document_type = normalize_document_type(document_type)

    text = clean_ocr_text(text)

    name = extract_name(
        text,
        document_type
    )

    document_number = extract_document_number(
        text,
        document_type
    )

    date_of_birth = extract_date_of_birth(text)

    gender = extract_gender(text)

    address = extract_address(text)

    return {
        "document_type": document_type or None,
        "name": name,
        "document_number": document_number,
        "date_of_birth": date_of_birth,
        "gender": gender,
        "address": address,
        "raw_text": text,
    }


# ============================================================
# OCR CONFIDENCE
# ============================================================

def calculate_confidence(
    text: str,
    fields: Dict
) -> float:

    if not text:
        return 0.0

    score = 20.0

    text_length = len(text.strip())

    if text_length >= 20:
        score += 20

    if text_length >= 60:
        score += 15

    if fields.get("name"):
        score += 15

    if fields.get("document_number"):
        score += 20

    if fields.get("date_of_birth"):
        score += 5

    if fields.get("gender"):
        score += 5

    return min(
        100.0,
        round(score, 2)
    )


# ============================================================
# OCR STATUS
# ============================================================

def determine_ocr_status(
    text: str,
    fields: Dict,
    document_type: Optional[str]
) -> str:

    if not text or len(text.strip()) < 5:
        return "OCR Failed"

    document_type = normalize_document_type(document_type)

    if document_type == "pan":

        if fields.get("document_number"):
            return "Verified"

        # PAN OCR may not detect the number on poor images,
        # but readable text was still found.
        if len(text) >= 20:
            return "Needs Review"

        return "OCR Failed"

    if document_type == "passport":

        if fields.get("document_number"):
            return "Verified"

        if len(text) >= 30:
            return "Needs Review"

        return "OCR Failed"

    if document_type == "voter_id":

        if fields.get("document_number"):
            return "Verified"

        if len(text) >= 20:
            return "Needs Review"

        return "OCR Failed"

    if len(text) >= 20:
        return "Needs Review"

    return "OCR Failed"


# ============================================================
# MAIN OCR PROCESSOR
# ============================================================

def process_ocr(
    image_path,
    document_type: Optional[str] = None
) -> Dict:

    document_type = normalize_document_type(document_type)

    diagnostics = get_ocr_status()

    if not diagnostics["pytesseract_installed"]:

        return {
            "document_type": document_type or None,
            "name": None,
            "document_number": None,
            "date_of_birth": None,
            "gender": None,
            "address": None,
            "raw_text": "",
            "confidence": 0.0,
            "status": "OCR Failed",
            "error": diagnostics["message"],
            "tesseract_available": False,
        }

    if not diagnostics["tesseract_available"]:

        return {
            "document_type": document_type or None,
            "name": None,
            "document_number": None,
            "date_of_birth": None,
            "gender": None,
            "address": None,
            "raw_text": "",
            "confidence": 0.0,
            "status": "OCR Failed",
            "error": diagnostics["message"],
            "tesseract_available": False,
        }

    try:

        raw_text = extract_text(
            image_path,
            document_type
        )

        raw_text = clean_ocr_text(raw_text)

        fields = extract_fields(
            raw_text,
            document_type
        )

        confidence = calculate_confidence(
            raw_text,
            fields
        )

        status = determine_ocr_status(
            raw_text,
            fields,
            document_type
        )

        return {
            **fields,
            "confidence": confidence,
            "status": status,
            "error": None,
            "tesseract_available": True,
        }

    except Exception as exc:

        return {
            "document_type": document_type or None,
            "name": None,
            "document_number": None,
            "date_of_birth": None,
            "gender": None,
            "address": None,
            "raw_text": "",
            "confidence": 0.0,
            "status": "OCR Failed",
            "error": str(exc),
            "tesseract_available": True,
        }


# ============================================================
# COMPATIBILITY FUNCTION
# ============================================================

def extract_document_data(
    image_path,
    document_type: Optional[str] = None
) -> Dict:

    return process_ocr(
        image_path,
        document_type
    )


# ============================================================
# SIMPLE ALIASES
# ============================================================

def extract_document_text(
    image_path,
    document_type: Optional[str] = None
) -> str:

    return extract_text(
        image_path,
        document_type
    )


def check_ocr() -> Dict:
    return get_ocr_status()


# ============================================================
# COMMAND-LINE TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("OCR SYSTEM CHECK")
    print("=" * 60)

    status = get_ocr_status()

    for key, value in status.items():
        print(f"{key}: {value}")

    print("=" * 60)