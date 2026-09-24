# ai_models/face_verification/face_utils.py

from pathlib import Path

import cv2
import numpy as np


IMAGE_SIZE = (224, 224)


def load_face_image(image_path):

    image_path = Path(
        image_path
    )

    if not image_path.exists():

        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    image = cv2.imread(
        str(image_path)
    )

    if image is None:

        raise ValueError(
            f"Unable to read image: {image_path}"
        )

    image = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2RGB
    )

    image = cv2.resize(
        image,
        IMAGE_SIZE
    )

    image = image.astype(
        np.float32
    )

    return image


def detect_face(image_path):

    image = cv2.imread(
        str(image_path)
    )

    if image is None:

        raise ValueError(
            "Unable to read image."
        )

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    cascade_path = (
        cv2.data.haarcascades +
        "haarcascade_frontalface_default.xml"
    )

    detector = cv2.CascadeClassifier(
        cascade_path
    )

    faces = detector.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(60, 60)
    )

    return faces


def crop_largest_face(image_path):

    image = cv2.imread(
        str(image_path)
    )

    if image is None:

        raise ValueError(
            "Unable to read image."
        )

    faces = detect_face(
        image_path
    )

    if len(faces) == 0:

        return None

    largest = max(
        faces,
        key=lambda face:
        face[2] * face[3]
    )

    x, y, width, height = largest

    face = image[
        y:y + height,
        x:x + width
    ]

    face = cv2.cvtColor(
        face,
        cv2.COLOR_BGR2RGB
    )

    face = cv2.resize(
        face,
        IMAGE_SIZE
    )

    return face.astype(
        np.float32
    )