# ai_models/forgery_detector/preprocessing.py

from pathlib import Path

import tensorflow as tf


IMAGE_SIZE = (224, 224)


IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp"
}


def is_image(file):

    return (
        file.is_file()
        and file.suffix.lower()
        in IMAGE_EXTENSIONS
    )


def collect_images(folder):

    folder = Path(folder)

    return [
        str(file)
        for file in folder.rglob("*")
        if is_image(file)
    ]


def load_image(path, label):

    image = tf.io.read_file(
        path
    )

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


def prepare_image(image_path):

    image = tf.keras.utils.load_img(
        image_path,
        target_size=IMAGE_SIZE
    )

    image = tf.keras.utils.img_to_array(
        image
    )

    image = tf.expand_dims(
        image,
        axis=0
    )

    return image