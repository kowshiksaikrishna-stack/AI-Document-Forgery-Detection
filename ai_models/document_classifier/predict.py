# ai_models/document_classifier/predict.py

from pathlib import Path
import json
import sys

import numpy as np
import tensorflow as tf


IMAGE_SIZE = (224, 224)

MODEL_DIR = (
    Path(__file__).resolve().parent /
    "model"
)

MODEL_PATH = (
    MODEL_DIR /
    "document_classifier.keras"
)

CLASS_NAMES_PATH = (
    MODEL_DIR /
    "class_names.json"
)


def load_model():

    if not MODEL_PATH.exists():

        raise FileNotFoundError(
            f"Model not found:\n{MODEL_PATH}\n"
            "Train the classifier first."
        )

    return tf.keras.models.load_model(
        MODEL_PATH
    )


def load_classes():

    if not CLASS_NAMES_PATH.exists():

        raise FileNotFoundError(
            f"Class file not found:\n"
            f"{CLASS_NAMES_PATH}"
        )

    with open(
        CLASS_NAMES_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def prepare_image(image_path):

    image = tf.keras.utils.load_img(
        image_path,
        target_size=IMAGE_SIZE
    )

    image = tf.keras.utils.img_to_array(
        image
    )

    image = np.expand_dims(
        image,
        axis=0
    )

    return image


def predict_document(image_path):

    model = load_model()

    class_names = load_classes()

    image = prepare_image(
        image_path
    )

    predictions = model.predict(
        image,
        verbose=0
    )[0]

    index = int(
        np.argmax(predictions)
    )

    confidence = float(
        predictions[index]
    )

    result = {
        "document_type": class_names[index],
        "confidence": round(
            confidence * 100,
            2
        ),
        "probabilities": {
            class_names[i]: round(
                float(predictions[i]) * 100,
                2
            )
            for i in range(len(class_names))
        }
    }

    return result


if __name__ == "__main__":

    if len(sys.argv) != 2:

        print(
            "Usage:"
        )

        print(
            "py predict.py <image_path>"
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

    result = predict_document(
        image_path
    )

    print()
    print("=" * 50)
    print("DOCUMENT PREDICTION")
    print("=" * 50)

    print(
        f"Document Type: "
        f"{result['document_type']}"
    )

    print(
        f"Confidence: "
        f"{result['confidence']}%"
    )

    print()
    print("Probabilities:")

    for name, probability in (
        result["probabilities"].items()
    ):

        print(
            f"{name}: {probability}%"
        )