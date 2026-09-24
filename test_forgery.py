from pathlib import Path
import sys

from backend.services.ai_service import detect_forgery


def main():
    print("=" * 70)
    print("FORGERY MODEL DIRECT TEST")
    print("=" * 70)

    if len(sys.argv) < 2:
        print()
        print("Usage:")
        print(
            'python test_forgery.py "FULL_PATH_TO_IMAGE"'
        )
        print()
        print("Example:")
        print(
            'python test_forgery.py "D:\\DUCUMENT-SCANNER\\AI_BASED\\dataset\\pan\\genuine\\image.jpg"'
        )
        return

    image_path = Path(sys.argv[1])

    if not image_path.exists():
        print()
        print("ERROR: Image not found.")
        print(f"Path: {image_path}")
        return

    if not image_path.is_file():
        print()
        print("ERROR: The supplied path is not a file.")
        return

    print()
    print(f"Image: {image_path}")
    print()

    try:
        result = detect_forgery(image_path)

        print("=" * 70)
        print("MODEL RESULT")
        print("=" * 70)

        print(
            f"Status:              {result.get('status')}"
        )

        print(
            f"Forgery score:       {result.get('forgery_score')}%"
        )

        print(
            f"Genuine probability: {result.get('genuine_probability')}%"
        )

        print(
            f"Fake probability:    {result.get('fake_probability')}%"
        )

        print(
            f"Classes:             {result.get('classes')}"
        )

        print(
            f"Message:             {result.get('message')}"
        )

        print("=" * 70)

    except Exception as error:
        print()
        print("=" * 70)
        print("MODEL ERROR")
        print("=" * 70)
        print(type(error).__name__)
        print(str(error))
        print("=" * 70)


if __name__ == "__main__":
    main()