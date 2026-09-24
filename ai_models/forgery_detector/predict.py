# ai_models/forgery_detector/predict.py

from pathlib import Path
import sys

from .predict_classifier import predict


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
            "Image not found."
        )

        sys.exit(1)

    result = predict(
        image_path
    )

    print()
    print("=" * 50)
    print("FORGERY DETECTION")
    print("=" * 50)

    print(
        f"Result: {result['result']}"
    )

    print(
        f"Confidence: "
        f"{result['confidence']}%"
    )

    print(
        f"Forgery Probability: "
        f"{result['forgery_probability']}%"
    )