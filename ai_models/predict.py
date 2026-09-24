# ai_models/predict.py

from pathlib import Path
import sys

from document_classifier.predict import (
    predict_document
)

from forgery_detector.predict_classifier import (
    predict as predict_forgery
)


def predict_document_system(
    image_path
):

    image_path = Path(
        image_path
    )

    document_result = predict_document(
        image_path
    )

    forgery_result = predict_forgery(
        image_path
    )

    return {
        "document_classification":
            document_result,

        "forgery_detection":
            forgery_result
    }


if __name__ == "__main__":

    if len(sys.argv) != 2:

        print(
            "Usage:"
        )

        print(
            "py predict.py <image>"
        )

        sys.exit(1)

    image_path = Path(
        sys.argv[1]
    )

    if not image_path.exists():

        print(
            f"Image not found: {image_path}"
        )

        sys.exit(1)

    result = predict_document_system(
        image_path
    )

    print()
    print("=" * 70)
    print("AI DOCUMENT VERIFICATION")
    print("=" * 70)

    print()
    print("DOCUMENT TYPE:")

    print(
        result[
            "document_classification"
        ][
            "document_type"
        ]
    )

    print(
        "Confidence:",
        result[
            "document_classification"
        ][
            "confidence"
        ],
        "%"
    )

    print()
    print("FORGERY RESULT:")

    print(
        result[
            "forgery_detection"
        ][
            "result"
        ]
    )

    print(
        "Confidence:",
        result[
            "forgery_detection"
        ][
            "confidence"
        ],
        "%"
    )