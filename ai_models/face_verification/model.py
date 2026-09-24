# ai_models/face_verification/model.py

from pathlib import Path

import tensorflow as tf
from tensorflow.keras import layers


IMAGE_SIZE = (224, 224)


def build_face_embedding_model():

    base_model = tf.keras.applications.MobileNetV2(
        input_shape=(224, 224, 3),
        include_top=False,
        weights="imagenet"
    )

    base_model.trainable = False

    inputs = layers.Input(
        shape=(224, 224, 3),
        name="face_image"
    )

    x = tf.keras.applications.mobilenet_v2.preprocess_input(
        inputs
    )

    x = base_model(
        x,
        training=False
    )

    x = layers.GlobalAveragePooling2D()(x)

    outputs = layers.Lambda(
        lambda value: tf.math.l2_normalize(
            value,
            axis=1
        )
    )(x)

    model = tf.keras.Model(
        inputs,
        outputs,
        name="face_verification"
    )

    return model


def save_model():

    model = build_face_embedding_model()

    model_dir = (
        Path(__file__).resolve().parent /
        "model"
    )

    model_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    model_path = (
        model_dir /
        "face_verification.keras"
    )

    model.save(
        model_path
    )

    return model_path


if __name__ == "__main__":

    path = save_model()

    print(
        f"Face model saved to: {path}"
    )