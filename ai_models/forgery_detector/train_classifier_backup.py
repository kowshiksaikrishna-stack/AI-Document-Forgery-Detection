from pathlib import Path
import json
import random

import numpy as np
import tensorflow as tf

from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.applications import MobileNetV2


# ============================================================
# CONFIGURATION
# ============================================================

SEED = 42

random.seed(SEED)
np.random.seed(SEED)
tf.random.set_seed(SEED)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_ROOT = PROJECT_ROOT / "dataset"

OUTPUT_DIR = (
    PROJECT_ROOT
    / "ai_models"
    / "forgery_detector"
    / "model"
)

MODEL_PATH = OUTPUT_DIR / "forgery_detector.keras"
CLASS_NAMES_PATH = OUTPUT_DIR / "class_names.json"
EVALUATION_PATH = OUTPUT_DIR / "evaluation.json"

IMAGE_SIZE = (224, 224)
BATCH_SIZE = 16

INITIAL_EPOCHS = 20
FINE_TUNE_EPOCHS = 20

TEST_SIZE = 0.15
VALIDATION_SIZE = 0.15

SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}

DOCUMENT_TYPES = [
    "pan",
    "passport",
    "voter_id",
]

CLASS_NAMES = [
    "genuine",
    "fake",
]

CLASS_TO_INDEX = {
    "genuine": 0,
    "fake": 1,
}


# ============================================================
# TENSORFLOW
# ============================================================

def configure_tensorflow():

    gpus = tf.config.list_physical_devices("GPU")

    if gpus:
        print("TensorFlow GPU devices:")
        for gpu in gpus:
            print(" ", gpu)

            try:
                tf.config.experimental.set_memory_growth(
                    gpu,
                    True
                )
            except RuntimeError:
                pass

    else:
        print("No TensorFlow GPU detected.")
        print("Training will use CPU.")


# ============================================================
# OUTPUT DIRECTORY
# ============================================================

def prepare_output_directory():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


# ============================================================
# DATASET COLLECTION
# ============================================================

def collect_dataset():

    image_paths = []
    labels = []
    document_types = []

    print()
    print("=" * 70)
    print("COLLECTING DATASET")
    print("=" * 70)

    if not DATASET_ROOT.exists():

        raise FileNotFoundError(
            f"Dataset directory not found:\n{DATASET_ROOT}"
        )

    for document_type in DOCUMENT_TYPES:

        document_dir = DATASET_ROOT / document_type

        if not document_dir.exists():

            print(
                f"WARNING: Missing directory: {document_dir}"
            )

            continue

        for class_name in CLASS_NAMES:

            class_dir = document_dir / class_name

            if not class_dir.exists():

                print(
                    f"WARNING: Missing directory: {class_dir}"
                )

                continue

            files = sorted(
                [
                    path
                    for path in class_dir.rglob("*")
                    if (
                        path.is_file()
                        and path.suffix.lower()
                        in SUPPORTED_EXTENSIONS
                    )
                ]
            )

            print(
                f"{document_type:12s} | "
                f"{class_name:8s} | "
                f"{len(files):5d}"
            )

            for image_path in files:

                image_paths.append(str(image_path))
                labels.append(CLASS_TO_INDEX[class_name])
                document_types.append(document_type)

    if not image_paths:

        raise RuntimeError(
            "No images found."
        )

    print()
    print("Total images:", len(image_paths))
    print("Genuine:", labels.count(0))
    print("Fake:", labels.count(1))

    return (
        np.array(image_paths),
        np.array(labels, dtype=np.int32),
        np.array(document_types)
    )


# ============================================================
# DATASET SPLIT
# ============================================================

def split_dataset(
    image_paths,
    labels,
    document_types
):

    indices = np.arange(len(image_paths))

    train_indices, temp_indices = train_test_split(
        indices,
        test_size=TEST_SIZE + VALIDATION_SIZE,
        random_state=SEED,
        stratify=labels
    )

    temp_labels = labels[temp_indices]

    validation_fraction = (
        VALIDATION_SIZE /
        (TEST_SIZE + VALIDATION_SIZE)
    )

    validation_indices, test_indices = train_test_split(
        temp_indices,
        test_size=1.0 - validation_fraction,
        random_state=SEED,
        stratify=temp_labels
    )

    return (
        image_paths[train_indices],
        labels[train_indices],
        document_types[train_indices],

        image_paths[validation_indices],
        labels[validation_indices],
        document_types[validation_indices],

        image_paths[test_indices],
        labels[test_indices],
        document_types[test_indices]
    )


# ============================================================
# IMAGE LOADING
# ============================================================

def load_image(path, label):

    image = tf.io.read_file(path)

    image = tf.image.decode_image(
        image,
        channels=3,
        expand_animations=False
    )

    image.set_shape([None, None, 3])

    image = tf.image.resize(
        image,
        IMAGE_SIZE,
        method=tf.image.ResizeMethod.BILINEAR
    )

    image = tf.cast(
        image,
        tf.float32
    )

    return image, label


# ============================================================
# SAFE DOCUMENT AUGMENTATION
# ============================================================

augmentation = keras.Sequential(
    [

        # Small rotation only.
        # NO horizontal flip.
        layers.RandomRotation(
            factor=0.015
        ),

        layers.RandomZoom(
            height_factor=(-0.03, 0.03),
            width_factor=(-0.03, 0.03)
        ),

        layers.RandomTranslation(
            height_factor=0.02,
            width_factor=0.02
        ),

        layers.RandomContrast(
            factor=0.08
        ),

    ],
    name="document_augmentation"
)


def augment_image(image, label):

    image = augmentation(
        image,
        training=True
    )

    return image, label


# ============================================================
# DATASET CREATION
# ============================================================

def create_dataset(
    paths,
    labels,
    training=False
):

    dataset = tf.data.Dataset.from_tensor_slices(
        (
            paths,
            labels
        )
    )

    if training:

        dataset = dataset.shuffle(
            buffer_size=len(paths),
            seed=SEED,
            reshuffle_each_iteration=True
        )

    dataset = dataset.map(
        load_image,
        num_parallel_calls=tf.data.AUTOTUNE
    )

    if training:

        dataset = dataset.map(
            augment_image,
            num_parallel_calls=tf.data.AUTOTUNE
        )

    dataset = dataset.batch(
        BATCH_SIZE
    )

    dataset = dataset.prefetch(
        tf.data.AUTOTUNE
    )

    return dataset


# ============================================================
# CLASS WEIGHTS
# ============================================================

def calculate_class_weights(labels):

    classes = np.unique(labels)

    weights = compute_class_weight(
        class_weight="balanced",
        classes=classes,
        y=labels
    )

    result = {
        int(class_id): float(weight)
        for class_id, weight
        in zip(classes, weights)
    }

    print()
    print("Class weights:")

    for class_id, weight in result.items():

        print(
            f"{CLASS_NAMES[class_id]}: {weight:.4f}"
        )

    return result


# ============================================================
# MODEL
# ============================================================

def build_model():

    base_model = MobileNetV2(
        include_top=False,
        weights="imagenet",
        input_shape=(224, 224, 3)
    )

    base_model.trainable = False

    inputs = keras.Input(
        shape=(224, 224, 3),
        name="document_image"
    )

    # MobileNetV2 preprocessing.
    x = layers.Rescaling(
        scale=1.0 / 127.5,
        offset=-1.0,
        name="mobilenet_preprocessing"
    )(inputs)

    x = base_model(
        x,
        training=False
    )

    x = layers.GlobalAveragePooling2D()(x)

    x = layers.BatchNormalization()(x)

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
        name="fake_probability"
    )(x)

    model = keras.Model(
        inputs,
        outputs,
        name="forgery_detector"
    )

    model.compile(
        optimizer=keras.optimizers.Adam(
            learning_rate=1e-3
        ),
        loss="binary_crossentropy",
        metrics=[
            keras.metrics.BinaryAccuracy(
                name="accuracy"
            ),
            keras.metrics.Precision(
                name="precision"
            ),
            keras.metrics.Recall(
                name="recall"
            ),
            keras.metrics.AUC(
                name="auc"
            )
        ]
    )

    return model, base_model


# ============================================================
# CALLBACKS
# ============================================================

def create_callbacks():

    return [

        keras.callbacks.ModelCheckpoint(
            filepath=str(MODEL_PATH),
            monitor="val_auc",
            mode="max",
            save_best_only=True,
            verbose=1
        ),

        keras.callbacks.EarlyStopping(
            monitor="val_auc",
            mode="max",
            patience=6,
            restore_best_weights=True,
            verbose=1
        ),

        keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.3,
            patience=2,
            min_lr=1e-7,
            verbose=1
        )
    ]


# ============================================================
# FINE TUNING
# ============================================================

def configure_fine_tuning(
    model,
    base_model
):

    base_model.trainable = True

    total_layers = len(base_model.layers)

    fine_tune_from = max(
        0,
        total_layers - 30
    )

    for index, layer in enumerate(
        base_model.layers
    ):

        layer.trainable = index >= fine_tune_from

        if isinstance(
            layer,
            layers.BatchNormalization
        ):

            layer.trainable = False

    model.compile(
        optimizer=keras.optimizers.Adam(
            learning_rate=1e-5
        ),
        loss="binary_crossentropy",
        metrics=[
            keras.metrics.BinaryAccuracy(
                name="accuracy"
            ),
            keras.metrics.Precision(
                name="precision"
            ),
            keras.metrics.Recall(
                name="recall"
            ),
            keras.metrics.AUC(
                name="auc"
            )
        ]
    )


# ============================================================
# EVALUATION
# ============================================================

def evaluate_model(
    model,
    test_paths,
    test_labels
):

    test_dataset = create_dataset(
        test_paths,
        test_labels,
        training=False
    )

    predictions = model.predict(
        test_dataset,
        verbose=1
    ).reshape(-1)

    predicted_labels = (
        predictions >= 0.5
    ).astype(np.int32)

    accuracy = accuracy_score(
        test_labels,
        predicted_labels
    )

    report = classification_report(
        test_labels,
        predicted_labels,
        target_names=CLASS_NAMES,
        digits=4,
        zero_division=0
    )

    matrix = confusion_matrix(
        test_labels,
        predicted_labels
    )

    print()
    print("=" * 70)
    print("TEST RESULTS")
    print("=" * 70)

    print(
        f"Accuracy: {accuracy * 100:.2f}%"
    )

    print()
    print(report)

    print("Confusion matrix:")
    print(matrix)

    return {
        "accuracy": float(accuracy),
        "classification_report": report,
        "confusion_matrix": matrix.tolist()
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 70)
    print("FORGERY DETECTOR TRAINING")
    print("=" * 70)

    configure_tensorflow()
    prepare_output_directory()

    (
        image_paths,
        labels,
        document_types
    ) = collect_dataset()

    (
        train_paths,
        train_labels,
        train_document_types,

        validation_paths,
        validation_labels,
        validation_document_types,

        test_paths,
        test_labels,
        test_document_types
    ) = split_dataset(
        image_paths,
        labels,
        document_types
    )

    print()
    print("Training:", len(train_paths))
    print("Validation:", len(validation_paths))
    print("Test:", len(test_paths))

    class_weights = calculate_class_weights(
        train_labels
    )

    train_dataset = create_dataset(
        train_paths,
        train_labels,
        training=True
    )

    validation_dataset = create_dataset(
        validation_paths,
        validation_labels,
        training=False
    )

    model, base_model = build_model()

    print()
    print("=" * 70)
    print("PHASE 1")
    print("=" * 70)

    model.fit(
        train_dataset,
        validation_data=validation_dataset,
        epochs=INITIAL_EPOCHS,
        class_weight=class_weights,
        callbacks=create_callbacks(),
        verbose=1
    )

    print()
    print("=" * 70)
    print("PHASE 2 - FINE TUNING")
    print("=" * 70)

    configure_fine_tuning(
        model,
        base_model
    )

    model.fit(
        train_dataset,
        validation_data=validation_dataset,
        epochs=FINE_TUNE_EPOCHS,
        class_weight=class_weights,
        callbacks=create_callbacks(),
        verbose=1
    )

    if MODEL_PATH.exists():

        model = keras.models.load_model(
            MODEL_PATH
        )

    else:

        model.save(
            MODEL_PATH
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

    evaluation = evaluate_model(
        model,
        test_paths,
        test_labels
    )

    with open(
        EVALUATION_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            evaluation,
            file,
            indent=4
        )

    print()
    print("=" * 70)
    print("TRAINING COMPLETED")
    print("=" * 70)

    print()
    print("Model:")
    print(MODEL_PATH)

    print()
    print("Evaluation:")
    print(EVALUATION_PATH)


if __name__ == "__main__":
    main()