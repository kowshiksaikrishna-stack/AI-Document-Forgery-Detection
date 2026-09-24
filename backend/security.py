import hashlib
import hmac
import secrets
from pathlib import Path


# ============================================================
# PASSWORD SECURITY
# ============================================================

def hash_password(password: str) -> str:
    """
    Create a salted SHA-256 password hash.

    This is suitable for the current project prototype.
    For production deployment, use Argon2id or bcrypt.
    """

    if not isinstance(password, str):
        raise TypeError("Password must be a string.")

    salt = secrets.token_hex(16)

    password_hash = hashlib.sha256(
        (salt + password).encode("utf-8")
    ).hexdigest()

    return f"{salt}${password_hash}"


def verify_password(
    password: str,
    stored_password: str
) -> bool:
    """
    Verify a password against a stored salted SHA-256 hash.
    """

    if not isinstance(password, str):
        return False

    if not isinstance(stored_password, str):
        return False

    try:
        salt, stored_hash = stored_password.split(
            "$",
            1
        )

        password_hash = hashlib.sha256(
            (salt + password).encode("utf-8")
        ).hexdigest()

        return hmac.compare_digest(
            password_hash,
            stored_hash
        )

    except Exception:
        return False


# ============================================================
# FILE HASHING
# ============================================================

def hash_file(file_path) -> str:
    """
    Generate a SHA-256 hash for a file.

    The hash is used to identify the exact uploaded document
    and can also be stored as an integrity record for the
    blockchain/audit layer.

    The document image itself is NOT stored on the blockchain.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {path}"
        )

    if not path.is_file():
        raise ValueError(
            f"Path is not a file: {path}"
        )

    sha256 = hashlib.sha256()

    with path.open("rb") as file:
        while True:
            chunk = file.read(1024 * 1024)

            if not chunk:
                break

            sha256.update(chunk)

    return sha256.hexdigest()


# ============================================================
# TEXT HASHING
# ============================================================

def hash_text(text: str) -> str:
    """
    Generate a SHA-256 hash from text.
    """

    if not isinstance(text, str):
        raise TypeError("Text must be a string.")

    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


# ============================================================
# GENERIC BYTES HASHING
# ============================================================

def hash_bytes(data: bytes) -> str:
    """
    Generate a SHA-256 hash from raw bytes.
    """

    if not isinstance(data, bytes):
        raise TypeError("Data must be bytes.")

    return hashlib.sha256(data).hexdigest()