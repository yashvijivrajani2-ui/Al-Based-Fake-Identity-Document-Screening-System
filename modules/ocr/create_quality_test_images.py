from pathlib import Path

import cv2


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PASSPORT_FOLDER = (
    PROJECT_ROOT
    / "datasets"
    / "sample_documents"
    / "passports"
)

INPUT_FILE = PASSPORT_FOLDER / "synthetic_valid_01.png"

BLURRY_OUTPUT_FILE = PASSPORT_FOLDER / "synthetic_blurry_01.png"

LOW_RESOLUTION_OUTPUT_FILE = (
    PASSPORT_FOLDER / "synthetic_low_resolution_01.png"
)

DARK_OUTPUT_FILE = PASSPORT_FOLDER / "synthetic_dark_01.png"

BRIGHT_OUTPUT_FILE = PASSPORT_FOLDER / "synthetic_bright_01.png"

ROTATED_OUTPUT_FILE = PASSPORT_FOLDER / "synthetic_rotated_01.png"

CROPPED_OUTPUT_FILE = PASSPORT_FOLDER / "synthetic_cropped_01.png"

GLARE_OUTPUT_FILE = PASSPORT_FOLDER / "synthetic_glare_01.png"


def save_image(output_file, image):
    saved = cv2.imwrite(str(output_file), image)

    if not saved:
        raise RuntimeError(
            f"Could not save image: {output_file}"
        )

    print(f"Created image: {output_file}")


def create_quality_test_images():
    image = cv2.imread(str(INPUT_FILE))

    if image is None:
        raise FileNotFoundError(
            f"Could not read source image: {INPUT_FILE}"
        )

    blurry_image = cv2.GaussianBlur(
        image,
        (21, 21),
        0
    )

    low_resolution_image = cv2.resize(
        image,
        (350, 225),
        interpolation=cv2.INTER_AREA
    )

    dark_image = cv2.convertScaleAbs(
        image,
        alpha=0.20,
        beta=0
    )

    bright_image = cv2.convertScaleAbs(
        image,
        alpha=1.0,
        beta=100
    )

    rotated_image = cv2.rotate(
        image,
        cv2.ROTATE_90_CLOCKWISE
    )

    cropped_image = image[
        150:750,
        0:700
    ]

    glare_image = image.copy()

    cv2.ellipse(
        glare_image,
        center=(700, 700),
        axes=(520, 160),
        angle=0,
        startAngle=0,
        endAngle=360,
        color=(255, 255, 255),
        thickness=-1
    )

   

    save_image(BLURRY_OUTPUT_FILE, blurry_image)
    save_image(
        LOW_RESOLUTION_OUTPUT_FILE,
        low_resolution_image
    )
    save_image(DARK_OUTPUT_FILE, dark_image)
    save_image(BRIGHT_OUTPUT_FILE, bright_image)
    save_image(ROTATED_OUTPUT_FILE, rotated_image)
    save_image(CROPPED_OUTPUT_FILE, cropped_image)
    save_image(GLARE_OUTPUT_FILE, glare_image)


if __name__ == "__main__":
    create_quality_test_images()