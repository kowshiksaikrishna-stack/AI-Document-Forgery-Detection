# ai_models/document_classifier/train_classifier.py

from pathlib import Path
import json

import tensorflow as tf


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_DIR = PROJECT_ROOT / "dataset"

MODEL_DIR = Path(__file__).resolve().parent / "model"

MODEL_PATH = MODEL_DIR / "document_classifier.keras"

CLASS_NAMES_PATH = MODEL_DIR / "class_names.json"

IMAGE_SIZE = (224, 224)

BATCH_SIZE = 16

EPOCHS = 15

SEED = 42

CLASS_NAMES = [
    "pan",
    "passport",
    "voter_id"
]


def check_dataset():

    if not DATASET_DIR.exists():

        raise FileNotFoundError(
            f"Dataset not found:\n{DATASET_DIR}"
        )

    for document_type in CLASS_NAMES:

        genuine = (
            DATASET_DIR /
            document_type /
            "genuine"
        )

        fake = (
            DATASET_DIR /
            document_type /
            "fake"
        )

        if not genuine.exists():

            raise FileNotFoundError(
                f"Missing folder:\n{genuine}"
            )

        if not fake.exists():

            raise FileNotFoundError(
                f"Missing folder:\n{fake}"
            )


def count_images(folder):

    extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".bmp",
        ".webp"
    }

    return sum(
        1
        for file in folder.rglob("*")
        if file.is_file()
        and file.suffix.lower() in extensions
    )


def show_dataset():

    print()
    print("=" * 60)
    print("DATASET")
    print("=" * 60)

    total = 0

    for document_type in CLASS_NAMES:

        genuine_count = count_images(
            DATASET_DIR /
            document_type /
            "genuine"
        )

        fake_count = count_images(
            DATASET_DIR /
            document_type /
            "fake"
        )

        current_total = (
            genuine_count +
            fake_count
        )

        total += current_total

        print(
            f"{document_type:<12}"
            f" genuine={genuine_count:<5}"
            f" fake={fake_count:<5}"
            f" total={current_total}"
        )

    print("-" * 60)

    print(
        f"Total images: {total}"
    )

    return total


def load_image(path, label):

    image = tf.io.read_file(path)

    image = tf.image.decode_image(
        image,
        channels=3,
        expand_animations=False
    )

    image.set_shape(
        [None, None, 3]
    )

    image = tf.image.resize(
        image,
        IMAGE_SIZE
    )

    image = tf.cast(
        image,
        tf.float32
    )

    return image, label


def collect_images():

    image_paths = []

    labels = []

    extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".bmp",
        ".webp"
    }

    for index, document_type in enumerate(
        CLASS_NAMES
    ):

        folder = (
            DATASET_DIR /
            document_type
        )

        for file in folder.rglob("*"):

            if (
                file.is_file()
                and file.suffix.lower()
                in extensions
            ):

                image_paths.append(
                    str(file)
                )

                labels.append(index)

    if not image_paths:

        raise RuntimeError(
            "No dataset images found."
        )

    return image_paths, labels


def build_model():

    base_model = tf.keras.applications.MobileNetV2(
        input_shape=(224, 224, 3),
        include_top=False,
        weights="imagenet"
    )

    base_model.trainable = False

    inputs = tf.keras.Input(
        shape=(224, 224, 3)
    )

    x = tf.keras.layers.RandomRotation(
        0.03
    )(inputs)

    x = tf.keras.layers.RandomZoom(
        0.08
    )(x)

    x = tf.keras.layers.RandomContrast(
        0.10
    )(x)

    x = tf.keras.applications.mobilenet_v2.preprocess_input(
        x
    )

    x = base_model(
        x,
        training=False
    )

    x = tf.keras.layers.GlobalAveragePooling2D()(x)

    x = tf.keras.layers.Dropout(
        0.30
    )(x)

    x = tf.keras.layers.Dense(
        128,
        activation="relu"
    )(x)

    x = tf.keras.layers.Dropout(
        0.20
    )(x)

    outputs = tf.keras.layers.Dense(
        3,
        activation="softmax"
    )(x)

    model = tf.keras.Model(
        inputs,
        outputs
    )

    model.compile(
        optimizer=tf.keras.optimizers.Adam(
            learning_rate=0.0001
        ),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )

    return model


def save_class_names():

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        CLASS_NAMES_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            CLASS_NAMES,
            file,
            indent=4
        )


def train():

    print()
    print("=" * 70)
    print("PAN / PASSPORT / VOTER ID")
    print("DOCUMENT CLASSIFIER TRAINING")
    print("=" * 70)

    print()
    print("Checking dataset...")

    check_dataset()

    print(
        f"Dataset path: {DATASET_DIR}"
    )

    total = show_dataset()

    if total < 6:

        raise RuntimeError(
            "Dataset contains too few images."
        )

    image_paths, labels = collect_images()

    dataset = tf.data.Dataset.from_tensor_slices(
        (
            image_paths,
            labels
        )
    )

    dataset = dataset.shuffle(
        len(image_paths),
        seed=SEED,
        reshuffle_each_iteration=False
    )

    dataset = dataset.map(
        load_image,
        num_parallel_calls=tf.data.AUTOTUNE
    )

    total_images = len(image_paths)

    train_count = int(
        total_images * 0.70
    )

    validation_count = int(
        total_images * 0.15
    )

    test_count = (
        total_images
        - train_count
        - validation_count
    )

    print()
    print(
        f"Training:   {train_count}"
    )

    print(
        f"Validation: {validation_count}"
    )

    print(
        f"Testing:    {test_count}"
    )

    train_dataset = dataset.take(
        train_count
    )

    remaining = dataset.skip(
        train_count
    )

    validation_dataset = remaining.take(
        validation_count
    )

    test_dataset = remaining.skip(
        validation_count
    )

    train_dataset = (
        train_dataset
        .batch(BATCH_SIZE)
        .prefetch(tf.data.AUTOTUNE)
    )

    validation_dataset = (
        validation_dataset
        .batch(BATCH_SIZE)
        .prefetch(tf.data.AUTOTUNE)
    )

    test_dataset = (
        test_dataset
        .batch(BATCH_SIZE)
        .prefetch(tf.data.AUTOTUNE)
    )

    print()
    print("Building model...")

    model = build_model()

    callbacks = [

        tf.keras.callbacks.ModelCheckpoint(
            str(MODEL_PATH),
            monitor="val_accuracy",
            save_best_only=True,
            verbose=1
        ),

        tf.keras.callbacks.EarlyStopping(
            monitor="val_loss",
            patience=4,
            restore_best_weights=True,
            verbose=1
        ),

        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=2,
            verbose=1
        )
    ]

    print()
    print("=" * 70)
    print("STARTING TRAINING")
    print("=" * 70)

    model.fit(
        train_dataset,
        validation_data=validation_dataset,
        epochs=EPOCHS,
        callbacks=callbacks
    )

    print()
    print("=" * 70)
    print("TESTING")
    print("=" * 70)

    loss, accuracy = model.evaluate(
        test_dataset,
        verbose=1
    )

    print(
        f"Test Loss: {loss:.4f}"
    )

    print(
        f"Test Accuracy: "
        f"{accuracy * 100:.2f}%"
    )

    model.save(
        MODEL_PATH
    )

    save_class_names()

    print()
    print(
        f"Model: {MODEL_PATH}"
    )

    print(
        f"Classes: {CLASS_NAMES_PATH}"
    )

    print()
    print("TRAINING COMPLETED")


if __name__ == "__main__":

    train()