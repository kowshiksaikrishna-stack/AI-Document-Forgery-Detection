# ocr/aadhaar_ocr.py

import re

def extract_aadhaar(image_bytes):

    return {
        "required_fields": [
            "name",
            "date_of_birth",
            "aadhaar_number"
        ],
        "fields": {
            "name": None,
            "date_of_birth": None,
            "aadhaar_number": None
        },
        "document_type": "Aadhaar Card"
    }