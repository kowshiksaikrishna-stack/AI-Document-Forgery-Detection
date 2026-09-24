from pathlib import Path

import cv2
import numpy as np
import tensorflow as tf
from PIL import Image

from backend.config import (
    FACE_MODEL,
    FACE_SIMILARITY_THRESHOLD,
    IMAGE_SIZE
)


# ============================================================
# MODEL
# ============================================================

_face_model = None


def load_face_model():
    """
    Load the face verification model once and reuse it.
    """

    global _face_model

    if _face_model is None:

        if not FACE_MODEL.exists():
            raise FileNotFoundError(
                "Face verification model not found: "
                f"{FACE_MODEL}"
            )

        _face_model = tf.keras.models.load_model(
            FACE_MODEL
        )

    return _face_model


# ============================================================
# FACE DETECTOR
# ============================================================

def get_face_detector():
    """
    Create OpenCV Haar Cascade face detector.
    """

    cascade_path = (
        cv2.data.haarcascades
        + "haarcascade_frontalface_default.xml"
    )

    detector = cv2.CascadeClassifier(
        cascade_path
    )

    if detector.empty():
        raise RuntimeError(
            "OpenCV face detector could not be loaded."
        )

    return detector


# ============================================================
# FACE EXTRACTION
# ============================================================

def extract_face(image_path):
    """
    Detect the largest face in an image.
    """

    image = cv2.imread(
        str(image_path)
    )

    if image is None:
        return None

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    detector = get_face_detector()

    faces = detector.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(60, 60)
    )

    if len(faces) == 0:
        return None

    x, y, width, height = max(
        faces,
        key=lambda face: face[2] * face[3]
    )

    face = image[
        y:y + height,
        x:x + width
    ]

    if face.size == 0:
        return None

    face = cv2.cvtColor(
        face,
        cv2.COLOR_BGR2RGB
    )

    return face


# ============================================================
# IMAGE PREPARATION
# ============================================================

def prepare_face(face):
    """
    Resize and normalize a detected face.
    """

    image = Image.fromarray(face)

    image = image.resize(
        IMAGE_SIZE
    )

    array = np.asarray(
        image,
        dtype=np.float32
    )

    array = array / 255.0

    return np.expand_dims(
        array,
        axis=0
    )


# ============================================================
# EMBEDDING NORMALIZATION
# ============================================================

def normalize_embedding(embedding):
    """
    L2-normalize a face embedding.
    """

    embedding = np.asarray(
        embedding,
        dtype=np.float32
    )

    norm = np.linalg.norm(
        embedding
    )

    if norm == 0:
        return embedding

    return embedding / norm


# ============================================================
# FACE EMBEDDING
# ============================================================

def get_embedding(image_path):
    """
    Detect a face and generate its model embedding.
    """

    model = load_face_model()

    face = extract_face(
        image_path
    )

    if face is None:
        return None

    prepared = prepare_face(
        face
    )

    embedding = model.predict(
        prepared,
        verbose=0
    )

    embedding = np.asarray(
        embedding,
        dtype=np.float32
    ).reshape(-1)

    return normalize_embedding(
        embedding
    )


# ============================================================
# COSINE SIMILARITY
# ============================================================

def cosine_similarity(
    first,
    second
):
    """
    Calculate cosine similarity between
    two face embeddings.
    """

    first = normalize_embedding(
        first
    )

    second = normalize_embedding(
        second
    )

    if first.size == 0:
        return 0.0

    if second.size == 0:
        return 0.0

    if first.shape != second.shape:
        return 0.0

    similarity = float(
        np.dot(
            first,
            second
        )
    )

    return similarity


# ============================================================
# FACE VERIFICATION
# ============================================================

def verify_faces(
    document_image,
    selfie_image
):
    """
    Compare the face on the identity document
    with the selfie.
    """

    if not document_image:

        return {
            "status": "Not Provided",
            "similarity_score": 0.0,
            "cosine_similarity": 0.0,
            "threshold": FACE_SIMILARITY_THRESHOLD,
            "message": (
                "Document image not provided"
            )
        }

    if not selfie_image:

        return {
            "status": "Not Provided",
            "similarity_score": 0.0,
            "cosine_similarity": 0.0,
            "threshold": FACE_SIMILARITY_THRESHOLD,
            "message": (
                "Selfie image not provided"
            )
        }

    try:

        document_embedding = get_embedding(
            document_image
        )

        selfie_embedding = get_embedding(
            selfie_image
        )

    except FileNotFoundError as error:

        return {
            "status": "Model Error",
            "similarity_score": 0.0,
            "cosine_similarity": 0.0,
            "threshold": FACE_SIMILARITY_THRESHOLD,
            "message": str(error)
        }

    except Exception as error:

        return {
            "status": "Verification Error",
            "similarity_score": 0.0,
            "cosine_similarity": 0.0,
            "threshold": FACE_SIMILARITY_THRESHOLD,
            "message": str(error)
        }

    if document_embedding is None:

        return {
            "status": "Face Not Detected",
            "similarity_score": 0.0,
            "cosine_similarity": 0.0,
            "threshold": FACE_SIMILARITY_THRESHOLD,
            "message": (
                "No face detected in "
                "the document image"
            )
        }

    if selfie_embedding is None:

        return {
            "status": "Face Not Detected",
            "similarity_score": 0.0,
            "cosine_similarity": 0.0,
            "threshold": FACE_SIMILARITY_THRESHOLD,
            "message": (
                "No face detected in "
                "the selfie image"
            )
        }

    similarity = cosine_similarity(
        document_embedding,
        selfie_embedding
    )

    # Convert cosine similarity from
    # approximately [-1, 1] to [0, 100].
    score = (
        (similarity + 1.0)
        / 2.0
        * 100.0
    )

    score = max(
        0.0,
        min(
            100.0,
            score
        )
    )

    threshold = (
        FACE_SIMILARITY_THRESHOLD
    )

    if similarity >= threshold:

        status = "MATCH"

        message = (
            "Face similarity is above "
            "the configured threshold."
        )

    else:

        status = "NO_MATCH"

        message = (
            "Face similarity is below "
            "the configured threshold."
        )

    return {
        "status": status,
        "similarity_score": round(
            score,
            2
        ),
        "cosine_similarity": round(
            similarity,
            4
        ),
        "threshold": threshold,
        "message": message
    }


# ============================================================
# COMPATIBILITY FUNCTION
# ============================================================

def verify_identity(
    document_image,
    selfie_image
):
    """
    Compatibility wrapper used by verification_service.py.

    The verification pipeline calls verify_identity(),
    while the underlying face comparison is performed
    by verify_faces().
    """

    return verify_faces(
        document_image=document_image,
        selfie_image=selfie_image
    )