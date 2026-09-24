# ai_models/train.py

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent


def run_training(
    script_path
):

    command = [
        sys.executable,
        str(script_path)
    ]

    subprocess.run(
        command,
        check=True
    )


def main():

    document_classifier = (
        PROJECT_ROOT /
        "document_classifier" /
        "train_classifier.py"
    )

    forgery_detector = (
        PROJECT_ROOT /
        "forgery_detector" /
        "train_classifier.py"
    )

    print()
    print("=" * 70)
    print("AI MODEL TRAINING")
    print("=" * 70)

    print()
    print("1. Document classifier")

    run_training(
        document_classifier
    )

    print()
    print("2. Forgery detector")

    run_training(
        forgery_detector
    )

    print()
    print("=" * 70)
    print("ALL TRAINING COMPLETED")
    print("=" * 70)


if __name__ == "__main__":

    main()