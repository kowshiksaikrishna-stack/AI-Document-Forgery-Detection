from fastapi import APIRouter, HTTPException

from backend.database import get_connection
from backend.models import RegisterRequest, LoginRequest
from backend.security import hash_password, verify_password


router = APIRouter()


# ============================================================
# REGISTER USER
# ============================================================

@router.post("/register")
def register_user(data: RegisterRequest):

    connection = None
    cursor = None

    try:
        connection = get_connection()

        cursor = connection.cursor(dictionary=True)

        # Check if email already exists
        cursor.execute(
            """
            SELECT id
            FROM users
            WHERE email = %s
            """,
            (str(data.email),)
        )

        existing_user = cursor.fetchone()

        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )

        # Hash password
        password_hash = hash_password(data.password)

        # Insert user
        cursor.execute(
            """
            INSERT INTO users
            (
                name,
                email,
                password_hash
            )
            VALUES
            (
                %s,
                %s,
                %s
            )
            """,
            (
                data.name,
                str(data.email),
                password_hash
            )
        )

        connection.commit()

        user_id = cursor.lastrowid

        return {
            "status": "success",
            "message": "User registered successfully",
            "user": {
                "id": user_id,
                "name": data.name,
                "email": str(data.email)
            }
        }

    except HTTPException:
        raise

    except Exception as error:

        if connection:
            connection.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Registration failed: {str(error)}"
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# LOGIN USER
# ============================================================

@router.post("/login")
def login_user(data: LoginRequest):

    connection = None
    cursor = None

    try:
        connection = get_connection()

        cursor = connection.cursor(dictionary=True)

        # Find user
        cursor.execute(
            """
            SELECT
                id,
                name,
                email,
                password_hash
            FROM users
            WHERE email = %s
            """,
            (str(data.email),)
        )

        user = cursor.fetchone()

        # User not found
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        # Verify password
        if not verify_password(
            data.password,
            user["password_hash"]
        ):
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        return {
            "status": "success",
            "message": "Login successful",
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"]
            }
        }

    except HTTPException:
        raise

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Login failed: {str(error)}"
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()