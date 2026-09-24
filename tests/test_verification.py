# tests/test_verification.py

from AI_BASED.backend.services.verification_service import verify_document

def test_supported_document():

    result = verify_document(
        "pan",
        b"test-document"
    )

    assert result["document_type"] == "pan"
    assert "risk_score" in result
    assert "blockchain_tx" in result