from pathlib import Path

from modules.ocr.image_quality import assess_image_quality


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PASSPORT_FOLDER = (
    PROJECT_ROOT
    / "datasets"
    / "sample_documents"
    / "passports"
)

IMAGE_FILES = [
    (
        "Clear valid image",
        PASSPORT_FOLDER / "synthetic_valid_01.png"
    ),
    (
        "Blurry image",
        PASSPORT_FOLDER / "synthetic_blurry_01.png"
    ),
    (
        "Low-resolution image",
        PASSPORT_FOLDER / "synthetic_low_resolution_01.png"
    ),
    (
        "Dark image",
        PASSPORT_FOLDER / "synthetic_dark_01.png"
    ),
    (
        "Bright image",
        PASSPORT_FOLDER / "synthetic_bright_01.png"
    ),
    (
        "Rotated image",
        PASSPORT_FOLDER / "synthetic_rotated_01.png"
    ),
]


def run_image_quality_test():
    for image_label, image_file in IMAGE_FILES:
        quality_result = assess_image_quality(image_file)

        print(f"\n{image_label}:")
        print(
            f"- quality_check_available: "
            f"{quality_result['quality_check_available']}"
        )
        print(f"- width: {quality_result['width']}")
        print(f"- height: {quality_result['height']}")
        print(f"- blur_score: {quality_result['blur_score']}")
        print(
            f"- brightness_score: "
            f"{quality_result['brightness_score']}"
        )
        print(
            f"- is_low_resolution: "
            f"{quality_result['is_low_resolution']}"
        )
        print(f"- is_blurry: {quality_result['is_blurry']}")
        print(f"- is_too_dark: {quality_result['is_too_dark']}")
        print(
            f"- is_too_bright: "
            f"{quality_result['is_too_bright']}"
        )
        print(
            f"- is_wrong_orientation: "
            f"{quality_result['is_wrong_orientation']}"
        )
        print(f"- error: {quality_result['error']}")


if __name__ == "__main__":
    run_image_quality_test()