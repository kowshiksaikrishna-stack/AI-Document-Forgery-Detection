# ai_models/forgery_detector/predict_classifier.py

from pathlib import Path
import sys

import numpy as np

try:
    import tensorflow as tf
except ImportError:
    tf = None

try:
    from ai_edge_litert.interpreter import Interpreter
except ImportError:
    Interpreter = None


MODEL_PATH = (
    Path(__file__).resolve().parent /
    "model" /
    "forgery_detector.keras"
)

TFLITE_MODEL_PATH = (
    Path(__file__).resolve().parent /
    "model" /
    "forgery_detector.tflite"
)


def predict(image_path):

    if not MODEL_PATH.exists():

        raise FileNotFoundError(
            f"Model not found: {MODEL_PATH}"
        )

    if tf is not None:
        model = tf.keras.models.load_model(MODEL_PATH)
        image = tf.keras.utils.load_img(image_path, target_size=(224, 224))
        image = tf.keras.utils.img_to_array(image)
        image = np.expand_dims(image, axis=0)
        probability = float(model.predict(image, verbose=0)[0][0])
    else:
        if Interpreter is None or not TFLITE_MODEL_PATH.exists():
            raise RuntimeError(
                "No TensorFlow or TensorFlow Lite forgery runtime is available."
            )

        from PIL import Image

        interpreter = Interpreter(model_path=str(TFLITE_MODEL_PATH))
        interpreter.allocate_tensors()
        input_details = interpreter.get_input_details()[0]
        output_details = interpreter.get_output_details()[0]
        image = Image.open(image_path).convert("RGB").resize((224, 224))
        image = np.expand_dims(np.asarray(image, dtype=np.float32), axis=0)
        interpreter.set_tensor(input_details["index"], image)
        interpreter.invoke()
        probability = float(
            interpreter.get_tensor(output_details["index"])[0][0]
        )

    if probability >= 0.5:

        result = "fake"

        confidence = probability

    else:

        result = "genuine"

        confidence = 1.0 - probability

    return {
        "result": result,
        "confidence": round(
            confidence * 100,
            2
        ),
        "forgery_probability": round(
            probability * 100,
            2
        )
    }


if __name__ == "__main__":

    if len(sys.argv) != 2:

        print(
            "Usage:"
        )

        print(
            "py predict_classifier.py <image>"
        )

        sys.exit(1)

    image_path = Path(
        sys.argv[1]
    )

    result = predict(
        image_path
    )

    print(
        result
    )