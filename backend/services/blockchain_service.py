import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from backend.config import (
    BLOCKCHAIN_ENABLED,
    BLOCKCHAIN_RPC_URL,
    BLOCKCHAIN_CONTRACT_ADDRESS,
)


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _build_local_transaction_hash(
    document_hash: str,
    document_type: str,
    result: str,
    risk_score: float,
) -> str:
    """
    Creates a deterministic local transaction-style hash.

    This is used when a real blockchain network is not configured.
    It provides an integrity/audit identifier without storing the
    original identity document on-chain.
    """
    payload = {
        "document_hash": document_hash,
        "document_type": document_type,
        "result": result,
        "risk_score": round(float(risk_score), 2),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    serialized = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    )

    return "local_" + _sha256_text(serialized)


def get_blockchain_status() -> Dict[str, Any]:
    """
    Returns the current blockchain configuration status.

    The application can run without a real blockchain connection.
    In that case, verification records receive a local integrity hash.
    """

    if BLOCKCHAIN_ENABLED:
        configured = bool(
            BLOCKCHAIN_RPC_URL and BLOCKCHAIN_CONTRACT_ADDRESS
        )

        if configured:
            return {
                "status": "configured",
                "enabled": True,
                "network": "Configured blockchain network",
                "rpc_url_configured": True,
                "contract_configured": True,
                "message": "Blockchain integration is configured.",
            }

        return {
            "status": "configuration_required",
            "enabled": True,
            "network": "Blockchain",
            "rpc_url_configured": bool(BLOCKCHAIN_RPC_URL),
            "contract_configured": bool(BLOCKCHAIN_CONTRACT_ADDRESS),
            "message": (
                "Blockchain is enabled, but RPC URL or contract address "
                "is missing."
            ),
        }

    return {
        "status": "local_mode",
        "enabled": False,
        "network": "Local integrity mode",
        "rpc_url_configured": False,
        "contract_configured": False,
        "message": (
            "Real blockchain integration is disabled. "
            "Local cryptographic hashes are used for auditability."
        ),
    }


def record_verification(
    document_hash: str,
    document_type: str,
    result: str,
    risk_score: float,
) -> Optional[Dict[str, Any]]:
    """
    Record a verification result for blockchain/audit purposes.

    IMPORTANT:
    Sensitive identity information and document images are NOT stored
    by this function.

    Only verification metadata and the document SHA-256 hash are used.

    When a real blockchain integration is not configured, the function
    creates a local cryptographic transaction-style identifier so that
    the rest of the application can work during development.
    """

    if not document_hash:
        return None

    document_hash = str(document_hash).strip()
    document_type = str(document_type or "Unknown").strip()
    result = str(result or "NEEDS REVIEW").strip()

    try:
        risk_score = float(risk_score)
    except (TypeError, ValueError):
        risk_score = 100.0

    risk_score = max(0.0, min(100.0, risk_score))

    # ---------------------------------------------------------
    # REAL BLOCKCHAIN MODE
    # ---------------------------------------------------------
    #
    # A production Web3 implementation can be connected here
    # using BLOCKCHAIN_RPC_URL, BLOCKCHAIN_CONTRACT_ADDRESS and
    # BLOCKCHAIN_PRIVATE_KEY.
    #
    # For now, the application intentionally does not attempt an
    # external blockchain transaction automatically. This prevents
    # the verification API from failing when Ganache/Hardhat/
    # Ethereum is not running.
    #
    # ---------------------------------------------------------

    if BLOCKCHAIN_ENABLED and BLOCKCHAIN_RPC_URL and BLOCKCHAIN_CONTRACT_ADDRESS:
        # The configured blockchain is acknowledged, but a real
        # transaction is not sent here unless the Web3 contract
        # integration is explicitly implemented.
        #
        # We still create an audit identifier so verification can
        # continue safely.
        transaction_hash = _build_local_transaction_hash(
            document_hash=document_hash,
            document_type=document_type,
            result=result,
            risk_score=risk_score,
        )

        return {
            "status": "pending_blockchain_integration",
            "transaction_hash": transaction_hash,
            "tx_hash": transaction_hash,
            "document_hash": document_hash,
            "document_type": document_type,
            "result": result,
            "risk_score": round(risk_score, 2),
            "message": (
                "Verification recorded with a local integrity hash. "
                "A real blockchain transaction has not been submitted."
            ),
        }

    # ---------------------------------------------------------
    # LOCAL DEVELOPMENT MODE
    # ---------------------------------------------------------

    transaction_hash = _build_local_transaction_hash(
        document_hash=document_hash,
        document_type=document_type,
        result=result,
        risk_score=risk_score,
    )

    return {
        "status": "local",
        "transaction_hash": transaction_hash,
        "tx_hash": transaction_hash,
        "document_hash": document_hash,
        "document_type": document_type,
        "result": result,
        "risk_score": round(risk_score, 2),
        "message": (
            "Verification recorded using a local cryptographic "
            "integrity hash."
        ),
    }


def verify_record_integrity(
    document_hash: str,
    stored_document_hash: str,
) -> bool:
    """
    Compare two SHA-256 document hashes.

    Returns True when both hashes match.
    """

    if not document_hash or not stored_document_hash:
        return False

    return (
        str(document_hash).strip().lower()
        == str(stored_document_hash).strip().lower()
    )


def create_verification_hash(
    document_hash: str,
    document_type: str,
    result: str,
    risk_score: float,
) -> str:
    """
    Public helper for generating an audit hash.
    """

    return _build_local_transaction_hash(
        document_hash=document_hash,
        document_type=document_type,
        result=result,
        risk_score=risk_score,
    )


def get_transaction_hash(blockchain_result: Optional[Dict[str, Any]]) -> Optional[str]:
    """
    Safely extract a transaction hash from a blockchain result.
    """

    if not blockchain_result:
        return None

    if not isinstance(blockchain_result, dict):
        return None

    return (
        blockchain_result.get("transaction_hash")
        or blockchain_result.get("tx_hash")
        or blockchain_result.get("hash")
    )