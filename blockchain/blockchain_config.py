# blockchain/blockchain_config.py

import os

BLOCKCHAIN_RPC_URL = os.getenv(
    "BLOCKCHAIN_RPC_URL",
    "http://127.0.0.1:8545"
)

CONTRACT_ADDRESS = os.getenv(
    "CONTRACT_ADDRESS",
    ""
)

PRIVATE_KEY = os.getenv(
    "BLOCKCHAIN_PRIVATE_KEY",
    ""
)