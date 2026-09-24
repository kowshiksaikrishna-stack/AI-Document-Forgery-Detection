# ocr/field_validation.py

import re

def validate_pan(value):
    if not value:
        return False

    return bool(
        re.fullmatch(
            r"[A-Z]{5}[0-9]{4}[A-Z]",
            value.upper()
        )
    )

def validate_aadhaar(value):
    if not value:
        return False

    digits = re.sub(r"\D", "", value)

    return len(digits) == 12

def validate_passport(value):
    if not value:
        return False

    return bool(
        re.fullmatch(
            r"[A-Z0-9]{6,9}",
            value.upper()
        )
    )

def validate_voterid(value):
    if not value:
        return False

    return len(value.strip()) >= 6