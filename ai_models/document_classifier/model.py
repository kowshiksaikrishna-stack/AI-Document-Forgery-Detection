# ai_models/document_classifier/model.py

from pathlib import Path

import tensorflow as tf
from tensorflow.keras import layers, models


IMAGE_SIZE = (224, 224)

NUM_CLASSES = 3


def build_document_classifier():

    base_model = tf.keras.applications.MobileNetV2(
        input_shape=(224, 224, 3),
        include_top=False,
        weights="imagenet"
    )

    base_model.trainable = False

    inputs = layers.Input(
        shape=(224, 224, 3),
        name="document_image"
    )

    x = layers.RandomRotation(0.03)(inputs)
    x = layers.RandomZoom(0.08)(x)
    x = layers.RandomContrast(0.10)(x)

    x = tf.keras.applications.mobilenet_v2.preprocess_input(x)

    x = base_model(
        x,
        training=False
    )

    x = layers.GlobalAveragePooling2D()(x)

    x = layers.Dropout(0.30)(x)

    x = layers.Dense(
        128,
        activation="relu"
    )(x)

    x = layers.Dropout(0.20)(x)

    outputs = layers.Dense(
        NUM_CLASSES,
        activation="softmax",
        name="document_type"
    )(x)

    model = models.Model(
        inputs=inputs,
        outputs=outputs,
        name="document_classifier"
    )

    model.compile(
        optimizer=tf.keras.optimizers.Adam(
            learning_rate=0.0001
        ),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )

    return model


def save_model():

    model_dir = Path(__file__).resolve().parent / "model"

    model_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    model_path = (
        model_dir /
        "document_classifier.keras"
    )

    model = build_document_classifier()

    model.save(model_path)

    return model_path


if __name__ == "__main__":

    path = save_model()

    print(
        f"Model saved to: {path}"
    )