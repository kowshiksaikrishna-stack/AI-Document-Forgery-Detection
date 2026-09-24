# ocr/voterid_ocr.py

def extract_voterid(image_bytes):

    return {
        "required_fields": [
            "name",
            "date_of_birth",
            "voter_id"
        ],
        "fields": {
            "name": None,
            "date_of_birth": None,
            "voter_id": None
        },
        "document_type": "Voter ID"
    }