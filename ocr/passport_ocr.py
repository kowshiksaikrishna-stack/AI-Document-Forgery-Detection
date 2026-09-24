# ocr/passport_ocr.py

def extract_passport(image_bytes):

    return {
        "required_fields": [
            "name",
            "passport_number",
            "nationality"
        ],
        "fields": {
            "name": None,
            "passport_number": None,
            "nationality": None
        },
        "document_type": "Passport"
    }