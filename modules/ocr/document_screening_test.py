from pathlib import Path

from modules.ocr.document_screening import screen_document
from modules.ocr.field_extractor import extract_passport_fields
from modules.ocr.image_ocr_reader import read_image_text
from modules.ocr.mrz_extractor import extract_mrz


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PASSPORT_FOLDER = (
    PROJECT_ROOT
    / "datasets"
    / "sample_documents"
    / "passports"
)

CLEAR_IMAGE_FILE = PASSPORT_FOLDER / "synthetic_valid_01.png"

TEST_IMAGES = [
    ("Clear valid image", CLEAR_IMAGE_FILE),
    ("Blurry image", PASSPORT_FOLDER / "synthetic_blurry_01.png"),
    (
        "Low-resolution image",
        PASSPORT_FOLDER / "synthetic_low_resolution_01.png"
    ),
    ("Dark image", PASSPORT_FOLDER / "synthetic_dark_01.png"),
    ("Bright image", PASSPORT_FOLDER / "synthetic_bright_01.png"),
    ("Rotated image", PASSPORT_FOLDER / "synthetic_rotated_01.png"),
]


def run_document_screening_test():
    ocr_result = read_image_text(CLEAR_IMAGE_FILE)

    if not ocr_result["success"]:
        print(f"OCR failed: {ocr_result['error']}")
        return

    passport_fields = extract_passport_fields(ocr_result["text_lines"])
    mrz_result = extract_mrz(ocr_result["text_lines"])

    for image_label, image_file in TEST_IMAGES:
        screening_result = screen_document(
            passport_fields=passport_fields,
            mrz_result=mrz_result,
            average_confidence=ocr_result["average_confidence"],
            image_path=image_file
        )

        quality_result = screening_result["image_quality"]

        print(f"\n{image_label}:")
        print(
            f"- review_required: "
            f"{screening_result['review_required']}"
        )
        print(f"- flag_count: {screening_result['flag_count']}")

        if quality_result:
            print(
                f"- is_low_resolution: "
                f"{quality_result['is_low_resolution']}"
            )
            print(f"- is_blurry: {quality_result['is_blurry']}")
            print(
                f"- is_too_dark: "
                f"{quality_result['is_too_dark']}"
            )
            print(
                f"- is_too_bright: "
                f"{quality_result['is_too_bright']}"
            )
            print(
                f"- is_wrong_orientation: "
                f"{quality_result['is_wrong_orientation']}"
            )

        print("- flags:")

        if not screening_result["flags"]:
            print("  No document flags found.")

        for flag in screening_result["flags"]:
            print(f"  {flag['code']}: {flag['message']}")


if __name__ == "__main__":
    run_document_screening_test()