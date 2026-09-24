from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.auth import router as auth_router
from backend.routes.documents import router as documents_router
from backend.routes.verification import router as verification_router
from backend.routes.blockchain import router as blockchain_router


app = FastAPI(
    title="AI Fake Identity Document Screening System",
    description=(
        "AI-based fake identity document screening system "
        "for PAN Card, Passport and Voter ID."
    ),
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://127.0.0.1:5501",
        "http://127.0.0.1:5502",
        "http://localhost:5500",
        "http://localhost:5501",
        "http://localhost:5502",
        "https://ai-document-forgery-detection-f6hf-q6tqnsj6x.vercel.app",
    ],
    allow_origin_regex=r"https://ai-document-forgery-detection-[a-z0-9-]+\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    auth_router,
    prefix="/api/auth",
    tags=["Authentication"]
)

app.include_router(
    documents_router,
    prefix="/api/documents",
    tags=["Documents"]
)

app.include_router(
    verification_router,
    prefix="/api/verification",
    tags=["Verification"]
)

app.include_router(
    blockchain_router,
    prefix="/api/blockchain",
    tags=["Blockchain"]
)


@app.get("/")
def home():
    return {
        "status": "success",
        "message": "AI Fake Identity Document Screening API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }