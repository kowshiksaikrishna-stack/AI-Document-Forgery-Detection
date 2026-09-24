# ocr/pan_ocr.py

def extract_pan(image_bytes):

    return {
        "required_fields": [
            "name",
            "date_of_birth",
            "pan_number"
        ],
        "fields": {
            "name": None,
            "date_of_birth": None,
            "pan_number": None
        },
        "document_type": "PAN Card"
    }