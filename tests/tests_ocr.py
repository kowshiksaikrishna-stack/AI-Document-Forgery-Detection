# tests/test_ocr.py

from ocr.field_validation import (
    validate_pan,
    validate_aadhaar,
    validate_passport,
    validate_voterid
)

def test_pan():
    assert validate_pan("ABCDE1234F")

def test_aadhaar():
    assert validate_aadhaar("123456789012")

def test_passport():
    assert validate_passport("A1234567")

def test_voterid():
    assert validate_voterid("ABC1234567")