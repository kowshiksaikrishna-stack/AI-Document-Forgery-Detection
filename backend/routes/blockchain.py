from fastapi import APIRouter

from backend.services.blockchain_service import (
    get_blockchain_status
)


router = APIRouter()


@router.get("/status")
def blockchain_status():

    return get_blockchain_status()