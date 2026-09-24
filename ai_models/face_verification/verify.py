# ai_models/face_verification/verify.py

from pathlib import Path
import sys

import numpy as np
import tensorflow as tf

from .face_utils import crop_largest_face


MODEL_PATH = (
    Path(__file__).resolve().parent /
    "model" /
    "face_verification.keras"
)


MATCH_THRESHOLD = 0.70


def load_model():

    if not MODEL_PATH.exists():

        raise FileNotFoundError(
            f"Face model not found:\n"
            f"{MODEL_PATH}"
        )

    return tf.keras.models.load_model(
        MODEL_PATH
    )


def get_embedding(
    model,
    image_path
):

    face = crop_largest_face(
        image_path
    )

    if face is None:

        raise ValueError(
            f"No face detected: {image_path}"
        )

    face = np.expand_dims(
        face,
        axis=0
    )

    embedding = model.predict(
        face,
        verbose=0
    )[0]

    return embedding


def cosine_similarity(
    first,
    second
):

    first_norm = np.linalg.norm(
        first
    )

    second_norm = np.linalg.norm(
        second
    )

    if (
        first_norm == 0
        or second_norm == 0
    ):

        return 0.0

    return float(
        np.dot(first, second) /
        (
            first_norm *
            second_norm
        )
    )


def verify_faces(
    document_face_path,
    selfie_path
):

    model = load_model()

    document_embedding = get_embedding(
        model,
        document_face_path
    )

    selfie_embedding = get_embedding(
        model,
        selfie_path
    )

    similarity = cosine_similarity(
        document_embedding,
        selfie_embedding
    )

    score = max(
        0.0,
        min(
            1.0,
            (similarity + 1.0) / 2.0
        )
    )

    matched = (
        score >= MATCH_THRESHOLD
    )

    return {
        "matched": matched,
        "similarity_score": round(
            score * 100,
            2
        ),
        "threshold": MATCH_THRESHOLD * 100
    }


if __name__ == "__main__":

    if len(sys.argv) != 3:

        print(
            "Usage:"
        )

        print(
            "py verify.py "
            "<document_face> "
            "<selfie>"
        )

        sys.exit(1)

    document_face = Path(
        sys.argv[1]
    )

    selfie = Path(
        sys.argv[2]
    )

    result = verify_faces(
        document_face,
        selfie
    )

    print()
    print("=" * 55)
    print("FACE VERIFICATION")
    print("=" * 55)

    print(
        f"Match: {result['matched']}"
    )

    print(
        f"Similarity: "
        f"{result['similarity_score']}%"
    )

    print(
        f"Threshold: "
        f"{result['threshold']}%"
    )