# AI-Based Document Forgery Detection and Verification System

**Smart India Hackathon problem statement:** `2026188`  
**Prototype status:** Working research and demonstration prototype

## 1. Problem and Proposed Solution

Identity-document forgery creates risk for public services, financial institutions, education, employment, and other verification workflows. Manual inspection is slow, inconsistent, and difficult to scale.

This project presents an AI-assisted document screening system that analyzes uploaded identity-document images and returns an explainable first-level assessment. It combines document classification, forgery detection, OCR field extraction, optional face verification, a web dashboard, and an audit-oriented blockchain interface.

The system is intended to support an authorized reviewer. It is not a replacement for official government or legal verification.

## 2. Prototype Objectives

- Detect potential forgery in identity-document images.
- Support PAN cards, passports, and voter ID documents.
- Return genuine and fake probabilities with a verification score.
- Extract and validate document fields using OCR modules.
- Support optional selfie/document face comparison.
- Preserve verification history for dashboard review.
- Provide a blockchain-ready audit layer without storing document images on-chain.
- Offer a simple browser-based workflow for demonstration and evaluation.

## 3. System Workflow

```text
User uploads document image
        |
        v
Frontend preview and validation
        |
        v
FastAPI verification API
        |
        +--> Document classifier
        +--> Forgery detector
        +--> OCR and field validation
        +--> Optional face verification
        +--> Audit/hash recording
        |
        v
Verification result and dashboard history
```

### Verification flow

1. The user selects a JPG, JPEG, PNG, or WEBP document image.
2. The frontend previews the selected file.
3. The backend stores the upload temporarily and runs the AI pipeline.
4. The system calculates the verification status, score, and probabilities.
5. OCR and validation services can extract fields such as name, document number, date of birth, and address where supported.
6. The result is shown in the verification result sheet.
7. A compact verification record is added to browser history for dashboard display.
8. The blockchain service creates a local integrity hash by default, or can be connected to an EVM-compatible network when configured.

## 4. Supported Documents and Inputs

| Document | Dataset directory | Supported image formats |
| --- | --- | --- |
| PAN Card | `dataset/pan/` | JPG, JPEG, PNG, WEBP |
| Passport | `dataset/passport/` | JPG, JPEG, PNG, WEBP |
| Voter ID | `dataset/voter_id/` | JPG, JPEG, PNG, WEBP |

The face-verification dataset is stored under `dataset/face/` and contains document-face and selfie-face samples.

## 5. AI and Security Components

### AI models

- `ai_models/document_classifier/`: document-type classification.
- `ai_models/forgery_detector/`: genuine/fake image classification.
- `ai_models/face_verification/`: optional face comparison workflow.
- TensorFlow/Keras model files are stored under each model's `model/` directory.

### OCR and validation

The `ocr/` package contains document-specific OCR modules for PAN, passport, voter ID, and Aadhaar-style workflows, together with field validation helpers.

### Audit and blockchain layer

The project does not store original identity images on-chain. It records only verification metadata and a document hash.

By default, the application runs in **local integrity mode** and generates a cryptographic audit identifier. A real blockchain transaction requires:

- An EVM-compatible RPC node.
- A deployed `DocumentVerification` contract.
- A configured contract address and wallet key.

The current status endpoint is:

```text
GET /api/blockchain/status
```

## 6. Technology Stack

- **Frontend:** HTML5, CSS3, JavaScript
- **Backend:** Python, FastAPI, Uvicorn
- **AI:** TensorFlow, Keras, OpenCV, Pillow
- **OCR:** Tesseract through `pytesseract`
- **Database support:** MySQL connector and SQL schema
- **Blockchain interface:** Solidity contract and Web3 configuration
- **Testing:** Python test modules and API/service checks
- **Development platform:** Windows, VS Code, modern web browser

## 7. Repository Structure

```text
AI_BASED/
├── ai_models/
│   ├── document_classifier/
│   ├── face_verification/
│   └── forgery_detector/
├── backend/
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── security.py
│   ├── routes/
│   └── services/
├── blockchain/
│   ├── blockchain_config.py
│   ├── deploy.py
│   └── contracts/DocumentVerification.sol
├── database/schema.sql
├── dataset/
├── frontend/
│   ├── dashboard.html
│   ├── verification.html
│   ├── login.html
│   ├── register.html
│   ├── profile.html
│   ├── css/
│   └── js/
├── ocr/
├── reports/
├── tests/
├── requirements.txt
└── README.md
```

## 8. Setup and Run

### Prerequisites

- Python 3.10 or newer.
- Tesseract OCR installed and available on `PATH` if OCR features are used.
- A modern browser.
- VS Code Live Server or another static frontend server.

### Install dependencies

From the project root:

```powershell
cd "D:\DUCUMENT-SCANNER\AI_BASED"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Start the backend

```powershell
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

API base URL:

```text
http://127.0.0.1:8000
```

Health check:

```text
http://127.0.0.1:8000/health
```

### Start the frontend

Open the `frontend` folder with VS Code Live Server. With the workspace configuration, the usual URL is:

```text
http://127.0.0.1:5500/frontend/verification.html
```

The workspace ignores `uploads/` for Live Server reloads so backend file uploads do not refresh the result page.

## 9. API Endpoints

### Verify a document

```text
POST /api/verification/verify
Content-Type: multipart/form-data
Field: document
```

Example response:

```json
{
  "status": "success",
  "verification_status": "REAL",
  "result": "REAL",
  "score": 81.03,
  "fake_probability": 18.97,
  "genuine_probability": 81.03,
  "forgery_status": "GENUINE",
  "message": "Analysis completed."
}
```

### Other API groups

- `GET /health` - backend health check.
- `/api/auth` - registration and login routes.
- `/api/documents` - document-related routes.
- `GET /api/blockchain/status` - blockchain/local audit configuration status.
- `/api/blockchain` - blockchain route group.

## 10. Blockchain Configuration

The default configuration is intentionally safe for local development:

```env
BLOCKCHAIN_ENABLED=false
BLOCKCHAIN_RPC_URL=
BLOCKCHAIN_CONTRACT_ADDRESS=
BLOCKCHAIN_PRIVATE_KEY=
```

For a local EVM test network, create a `.env` file in the project root and set:

```env
BLOCKCHAIN_ENABLED=true
BLOCKCHAIN_RPC_URL=http://127.0.0.1:8545
BLOCKCHAIN_CONTRACT_ADDRESS=your_deployed_contract_address
BLOCKCHAIN_PRIVATE_KEY=your_test_wallet_private_key
```

Never commit a real private key or production credentials. Use a disposable development wallet and test network only.

## 11. Testing

Run the available tests from the project root:

```powershell
python -m pytest
```

Useful manual checks:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/api/blockchain/status
```

The prototype should be evaluated with both genuine and fake samples and with unsupported or invalid files to confirm error handling.

## 12. Limitations and Responsible Use

- Model predictions depend on training-data coverage and image quality.
- A result of `REAL` is an AI screening result, not proof of legal authenticity.
- OCR may fail on low-resolution, rotated, damaged, or poorly lit images.
- The default blockchain mode is a local cryptographic audit mode, not a live public-chain transaction.
- Authentication, database, and production deployment settings require additional hardening before real-world use.
- Sensitive identity documents should be protected with access control, encryption, retention limits, and secure deletion policies.

## 13. Future Scope

- Expand and rebalance the training dataset.
- Add document-specific tamper localization and explainable heatmaps.
- Improve OCR for regional languages and difficult image conditions.
- Add secure reviewer workflows and role-based access control.
- Complete contract deployment and transaction verification for a selected test network.
- Add automated API, UI, and model regression testing.
- Package the system for secure cloud or institutional deployment.

## 14. Project Context

This repository is a prototype submission aligned with Smart India Hackathon problem statement `2026188`. It demonstrates a complete flow from document upload to AI-assisted screening, result presentation, audit recording, and review history. The implementation is designed to be extended with stronger datasets, production security, and an approved institutional verification workflow.

## License

This project is intended for educational, research, and prototype demonstration purposes.
