import random
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATASET_DIR = PROJECT_ROOT / "dataset"

RANDOM_SEED = 42

random.seed(RANDOM_SEED)


# Number of synthetic images to generate
GENUINE_IMAGES_PER_TYPE = 100
FAKE_IMAGES_PER_TYPE = 100


IMAGE_WIDTH = 1000
IMAGE_HEIGHT = 650


DOCUMENT_TYPES = [
    "pan",
    "passport",
    "voter_id"
]


# ============================================================
# FONTS
# ============================================================

def get_font(size, bold=False):

    windows_fonts = [
        Path("C:/Windows/Fonts/arialbd.ttf")
        if bold
        else Path("C:/Windows/Fonts/arial.ttf"),

        Path("C:/Windows/Fonts/calibrib.ttf")
        if bold
        else Path("C:/Windows/Fonts/calibri.ttf"),

        Path("C:/Windows/Fonts/timesbd.ttf")
        if bold
        else Path("C:/Windows/Fonts/times.ttf")
    ]

    for font_path in windows_fonts:

        if font_path.exists():

            return ImageFont.truetype(
                str(font_path),
                size
            )

    return ImageFont.load_default()


FONT_SMALL = get_font(24)

FONT_NORMAL = get_font(30)

FONT_MEDIUM = get_font(38, bold=True)

FONT_LARGE = get_font(52, bold=True)


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def random_name():

    first_names = [
        "ARUN",
        "RAHUL",
        "PRIYA",
        "ANITA",
        "KARTHIK",
        "DIVYA",
        "ROHIT",
        "NEHA",
        "VIKAS",
        "POOJA",
        "AMIT",
        "SNEHA",
        "MANOJ",
        "KAVYA",
        "SANJAY"
    ]

    last_names = [
        "KUMAR",
        "SHARMA",
        "REDDY",
        "PATEL",
        "SINGH",
        "RAO",
        "VERMA",
        "NAIR",
        "DAS",
        "GUPTA"
    ]

    return (
        random.choice(first_names)
        + " "
        + random.choice(last_names)
    )


def random_date():

    day = random.randint(1, 28)

    month = random.randint(1, 12)

    year = random.randint(1970, 2003)

    return f"{day:02d}/{month:02d}/{year}"


def random_pan_number():

    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    return (
        "".join(random.choice(letters) for _ in range(5))
        + str(random.randint(1000, 9999))
        + random.choice(letters)
    )


def random_passport_number():

    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    return (
        random.choice(letters)
        + "".join(
            random.choice("0123456789")
            for _ in range(7)
        )
    )


def random_voter_number():

    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    return (
        "".join(
            random.choice(letters)
            for _ in range(3)
        )
        + str(random.randint(1000000, 9999999))
    )


def random_address():

    streets = [
        "MG ROAD",
        "MAIN ROAD",
        "GANDHI STREET",
        "LAKE VIEW ROAD",
        "PARK STREET",
        "TEMPLE ROAD",
        "MARKET ROAD"
    ]

    cities = [
        "CHENNAI",
        "HYDERABAD",
        "BENGALURU",
        "VIJAYAWADA",
        "VISAKHAPATNAM",
        "KAKINADA",
        "DELHI"
    ]

    return (
        f"{random.randint(1, 999)} "
        f"{random.choice(streets)}, "
        f"{random.choice(cities)}"
    )


# ============================================================
# IMAGE BACKGROUND
# ============================================================

def create_document_background():

    image = Image.new(
        "RGB",
        (
            IMAGE_WIDTH,
            IMAGE_HEIGHT
        ),
        "white"
    )

    draw = ImageDraw.Draw(image)

    # Outer border
    draw.rectangle(
        (
            15,
            15,
            IMAGE_WIDTH - 15,
            IMAGE_HEIGHT - 15
        ),
        outline=(40, 40, 40),
        width=5
    )

    # Inner border
    draw.rectangle(
        (
            30,
            30,
            IMAGE_WIDTH - 30,
            IMAGE_HEIGHT - 30
        ),
        outline=(130, 130, 130),
        width=2
    )

    # Security-style background lines
    for y in range(
        80,
        IMAGE_HEIGHT - 50,
        35
    ):

        draw.line(
            (
                40,
                y,
                IMAGE_WIDTH - 40,
                y
            ),
            fill=(235, 235, 235),
            width=1
        )

    return image


# ============================================================
# PAN CARD
# ============================================================

def create_pan_document(index):

    image = create_document_background()

    draw = ImageDraw.Draw(image)

    name = random_name()

    dob = random_date()

    pan_number = random_pan_number()

    draw.text(
        (70, 65),
        "INCOME TAX DEPARTMENT",
        font=FONT_MEDIUM,
        fill=(20, 20, 20)
    )

    draw.text(
        (70, 125),
        "PAN CARD",
        font=FONT_LARGE,
        fill=(30, 30, 30)
    )

    draw.text(
        (70, 220),
        "Permanent Account Number",
        font=FONT_NORMAL,
        fill=(70, 70, 70)
    )

    draw.text(
        (70, 290),
        "Name",
        font=FONT_SMALL,
        fill=(90, 90, 90)
    )

    draw.text(
        (250, 285),
        name,
        font=FONT_NORMAL,
        fill=(20, 20, 20)
    )

    draw.text(
        (70, 360),
        "PAN Number",
        font=FONT_SMALL,
        fill=(90, 90, 90)
    )

    draw.text(
        (250, 355),
        pan_number,
        font=FONT_MEDIUM,
        fill=(20, 20, 20)
    )

    draw.text(
        (70, 430),
        "Date of Birth",
        font=FONT_SMALL,
        fill=(90, 90, 90)
    )

    draw.text(
        (250, 425),
        dob,
        font=FONT_NORMAL,
        fill=(20, 20, 20)
    )

    # Synthetic photo placeholder
    draw.rectangle(
        (730, 190, 900, 400),
        outline=(60, 60, 60),
        width=3
    )

    draw.ellipse(
        (780, 220, 850, 290),
        outline=(60, 60, 60),
        width=3
    )

    draw.arc(
        (750, 280, 880, 390),
        180,
        360,
        fill=(60, 60, 60),
        width=3
    )

    draw.text(
        (70, 520),
        "SYNTHETIC SAMPLE - FOR RESEARCH USE ONLY",
        font=FONT_SMALL,
        fill=(120, 120, 120)
    )

    return image


# ============================================================
# PASSPORT
# ============================================================

def create_passport_document(index):

    image = create_document_background()

    draw = ImageDraw.Draw(image)

    name = random_name()

    dob = random_date()

    passport_number = random_passport_number()

    draw.text(
        (70, 60),
        "REPUBLIC OF INDIA",
        font=FONT_MEDIUM,
        fill=(20, 20, 20)
    )

    draw.text(
        (70, 120),
        "PASSPORT",
        font=FONT_LARGE,
        fill=(30, 30, 30)
    )

    draw.text(
        (70, 215),
        "Type",
        font=FONT_SMALL,
        fill=(90, 90, 90)
    )

    draw.text(
        (250, 210),
        "P",
        font=FONT_NORMAL,
        fill=(20, 20, 20)
    )

    draw.text(
        (70, 275),
        "Passport Number",
        font=FONT_SMALL,
        fill=(90, 90, 90)
    )

    draw.text(
        (300, 270),
        passport_number,
        font=FONT_MEDIUM,
        fill=(20, 20, 20)
    )

    draw.text(
        (70, 350),
        "Name",
        font=FONT_SMALL,
        fill=(90, 90, 90)
    )

    draw.text(
        (250, 345),
        name,
        font=FONT_NORMAL,
        fill=(20, 20, 20)
    )

    draw.text(
        (70, 425),
        "Date of Birth",
        font=FONT_SMALL,
        fill=(90, 90, 90)
    )

    draw.text(
        (250, 420),
        dob,
        font=FONT_NORMAL,
        fill=(20, 20, 20)
    )

    # Synthetic photo
    draw.rectangle(
        (730, 190, 900, 400),
        outline=(60, 60, 60),
        width=3
    )

    draw.ellipse(
        (780, 220, 850, 290),
        outline=(60, 60, 60),
        width=3
    )

    draw.arc(
        (750, 280, 880, 390),
        180,
        360,
        fill=(60, 60, 60),
        width=3
    )

    draw.text(
        (70, 520),
        "SYNTHETIC SAMPLE - FOR RESEARCH USE ONLY",
        font=FONT_SMALL,
        fill=(120, 120, 120)
    )

    return image


# ============================================================
# VOTER ID
# ============================================================

def create_voter_document(index):

    image = create_document_background()

    draw = ImageDraw.Draw(image)

    name = random_name()

    dob = random_date()

    voter_number = random_voter_number()

    address = random_address()

    draw.text(
        (70, 60),
        "ELECTION COMMISSION",
        font=FONT_MEDIUM,
        fill=(20, 20, 20)
    )

    draw.text(
        (70, 120),
        "VOTER ID",
        font=FONT_LARGE,
        fill=(30, 30, 30)
    )

    draw.text(
        (70, 215),
        "Elector Name",
        font=FONT_SMALL,
        fill=(90, 90, 90)
    )

    draw.text(
        (280, 210),
        name,
        font=FONT_NORMAL,
        fill=(20, 20, 20)
    )

    draw.text(
        (70, 280),
        "Voter ID Number",
        font=FONT_SMALL,
        fill=(90, 90, 90)
    )

    draw.text(
        (300, 275),
        voter_number,
        font=FONT_MEDIUM,
        fill=(20, 20, 20)
    )

    draw.text(
        (70, 350),
        "Date of Birth",
        font=FONT_SMALL,
        fill=(90, 90, 90)
    )

    draw.text(
        (280, 345),
        dob,
        font=FONT_NORMAL,
        fill=(20, 20, 20)
    )

    draw.text(
        (70, 420),
        "Address",
        font=FONT_SMALL,
        fill=(90, 90, 90)
    )

    draw.text(
        (250, 415),
        address,
        font=FONT_SMALL,
        fill=(20, 20, 20)
    )

    # Synthetic photo
    draw.rectangle(
        (730, 190, 900, 400),
        outline=(60, 60, 60),
        width=3
    )

    draw.ellipse(
        (780, 220, 850, 290),
        outline=(60, 60, 60),
        width=3
    )

    draw.arc(
        (750, 280, 880, 390),
        180,
        360,
        fill=(60, 60, 60),
        width=3
    )

    draw.text(
        (70, 520),
        "SYNTHETIC SAMPLE - FOR RESEARCH USE ONLY",
        font=FONT_SMALL,
        fill=(120, 120, 120)
    )

    return image


# ============================================================
# CREATE FAKE IMAGE
# ============================================================

def create_fake_version(image):

    fake = image.copy()

    draw = ImageDraw.Draw(fake)

    manipulation_type = random.choice(
        [
            "text_edit",
            "blur",
            "noise",
            "rotation",
            "contrast"
        ]
    )

    if manipulation_type == "text_edit":

        x = random.randint(
            250,
            550
        )

        y = random.randint(
            250,
            450
        )

        draw.rectangle(
            (
                x,
                y,
                x + 250,
                y + 45
            ),
            fill=(245, 245, 245)
        )

        draw.text(
            (
                x,
                y
            ),
            "MODIFIED",
            font=FONT_SMALL,
            fill=(180, 0, 0)
        )

    elif manipulation_type == "blur":

        fake = fake.filter(
            ImageFilter.GaussianBlur(
                radius=2
            )
        )

    elif manipulation_type == "noise":

        draw = ImageDraw.Draw(fake)

        for _ in range(3000):

            x = random.randint(
                0,
                IMAGE_WIDTH - 1
            )

            y = random.randint(
                0,
                IMAGE_HEIGHT - 1
            )

            value = random.randint(
                0,
                255
            )

            draw.point(
                (x, y),
                fill=(
                    value,
                    value,
                    value
                )
            )

    elif manipulation_type == "rotation":

        fake = fake.rotate(
            random.uniform(
                -3,
                3
            ),
            expand=False,
            fillcolor="white"
        )

    elif manipulation_type == "contrast":

        fake = fake.point(
            lambda pixel: min(
                255,
                max(
                    0,
                    int(
                        pixel * random.uniform(
                            0.65,
                            1.35
                        )
                    )
                )
            )
        )

    return fake


# ============================================================
# GENERATE DOCUMENT DATASET
# ============================================================

def generate_document_dataset():

    generators = {
        "pan": create_pan_document,
        "passport": create_passport_document,
        "voter_id": create_voter_document
    }

    for document_type in DOCUMENT_TYPES:

        genuine_dir = (
            DATASET_DIR
            / document_type
            / "genuine"
        )

        fake_dir = (
            DATASET_DIR
            / document_type
            / "fake"
        )

        genuine_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        fake_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        generator = generators[
            document_type
        ]

        print(
            f"\nGenerating {document_type} dataset..."
        )

        for index in range(
            1,
            GENUINE_IMAGES_PER_TYPE + 1
        ):

            image = generator(index)

            genuine_path = (
                genuine_dir
                / f"{document_type}_genuine_{index:04d}.png"
            )

            image.save(
                genuine_path
            )

            fake_image = create_fake_version(
                image
            )

            fake_path = (
                fake_dir
                / f"{document_type}_fake_{index:04d}.png"
            )

            fake_image.save(
                fake_path
            )

        print(
            f"Created "
            f"{GENUINE_IMAGES_PER_TYPE} genuine "
            f"and "
            f"{FAKE_IMAGES_PER_TYPE} fake images."
        )


# ============================================================
# FACE DATASET PLACEHOLDERS
# ============================================================

def create_face_directories():

    document_faces = (
        DATASET_DIR
        / "face"
        / "document_faces"
    )

    selfie_faces = (
        DATASET_DIR
        / "face"
        / "selfie_faces"
    )

    document_faces.mkdir(
        parents=True,
        exist_ok=True
    )

    selfie_faces.mkdir(
        parents=True,
        exist_ok=True
    )

    print(
        "\nFace dataset directories created."
    )

    print(
        "Add consented/authorized face images "
        "to these folders later."
    )


# ============================================================
# DATASET README
# ============================================================

def create_dataset_readme():

    readme_path = (
        DATASET_DIR
        / "DATASET_INFO.txt"
    )

    content = """
AI FAKE IDENTITY DOCUMENT SCREENING
===================================

SUPPORTED DOCUMENT TYPES
------------------------
1. PAN Card
2. Passport
3. Voter ID


GENERATED DATA
--------------
The document images generated by generate_dataset.py
are synthetic research samples.

They are NOT real government identity documents.

They must NOT be used as real identity documents.


DIRECTORY STRUCTURE
-------------------

dataset/
├── pan/
│   ├── genuine/
│   └── fake/
│
├── passport/
│   ├── genuine/
│   └── fake/
│
├── voter_id/
│   ├── genuine/
│   └── fake/
│
└── face/
    ├── document_faces/
    └── selfie_faces/


GENUINE
-------
Synthetic documents generated with the normal
synthetic template.


FAKE
----
Synthetic documents containing controlled
artificial modifications.

Examples:
- text modification
- blur
- noise
- rotation
- contrast modification


IMPORTANT
---------
This dataset is intended for a college/project
prototype.

It is not a production-grade identity verification
dataset and should not be used to claim real-world
government-document authentication accuracy.
"""

    with open(
        readme_path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            content.strip()
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 65)
    print(
        "AI FAKE IDENTITY DOCUMENT SCREENING"
    )
    print(
        "SYNTHETIC DATASET GENERATOR"
    )
    print("=" * 65)

    print(
        f"\nDataset directory:"
        f"\n{DATASET_DIR}"
    )

    print(
        "\nSupported documents:"
    )

    for document_type in DOCUMENT_TYPES:

        print(
            f" - {document_type}"
        )

    print(
        "\nCreating directories..."
    )

    generate_document_dataset()

    create_face_directories()

    create_dataset_readme()

    print()
    print("=" * 65)
    print("DATASET GENERATION COMPLETED")
    print("=" * 65)

    print(
        "\nYour dataset is now available at:"
    )

    print(
        DATASET_DIR
    )

    print(
        "\nNext step:"
    )

    print(
        "Train the document classifier."
    )

    print(
        "Then train the forgery detector."
    )


if __name__ == "__main__":

    main()