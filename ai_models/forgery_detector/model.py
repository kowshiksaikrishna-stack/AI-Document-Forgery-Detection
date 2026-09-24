# ai_models/forgery_detector/model.py

import tensorflow as tf
from tensorflow.keras import layers


def build_forgery_detector():

    base_model = tf.keras.applications.MobileNetV2(
        input_shape=(224, 224, 3),
        include_top=False,
        weights="imagenet"
    )

    base_model.trainable = False

    inputs = layers.Input(
        shape=(224, 224, 3)
    )

    x = layers.RandomRotation(
        0.02
    )(inputs)

    x = layers.RandomZoom(
        0.05
    )(x)

    x = tf.keras.applications.mobilenet_v2.preprocess_input(
        x
    )

    x = base_model(
        x,
        training=False
    )

    x = layers.GlobalAveragePooling2D()(x)

    x = layers.Dropout(
        0.30
    )(x)

    x = layers.Dense(
        128,
        activation="relu"
    )(x)

    x = layers.Dropout(
        0.20
    )(x)

    outputs = layers.Dense(
        1,
        activation="sigmoid",
        name="forgery_probability"
    )(x)

    model = tf.keras.Model(
        inputs,
        outputs,
        name="forgery_detector"
    )

    model.compile(
        optimizer=tf.keras.optimizers.Adam(
            learning_rate=0.0001
        ),
        loss="binary_crossentropy",
        metrics=["accuracy"]
    )

    return model