import argparse
from pathlib import Path

from modules.ocr.document_screening import screen_document
from modules.ocr.field_extractor import extract_passport_fields
from modules.ocr.image_ocr_reader import read_image_text, read_mrz_text
from modules.ocr.mrz_extractor import extract_mrz
from modules.ocr.result_writer import save_document_screening_result


PROJECT_ROOT = Path(__file__).resolve().parents[2]


DEFAULT_IMAGE_FILE = (
    PROJECT_ROOT
    / "datasets"
    / "sample_documents"
    / "passports"
    / "synthetic_valid_01.png"
)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Run passport OCR and document screening."
    )

    parser.add_argument(
        "image_path",
        nargs="?",
        default=str(DEFAULT_IMAGE_FILE),
        help="Path to the passport image to screen.",
    )

    return parser.parse_args()


def print_screening_summary(screening_result):
    print("\nDocument screening result:")
    print(
        f"- review_required: "
        f"{screening_result['review_required']}"
    )
    print(f"- flag_count: {screening_result['flag_count']}")

    checksum_result = screening_result["mrz_checksum"]
    print(
        f"- mrz_checksum_valid: "
        f"{checksum_result['checksum_valid']}"
    )

    quality_result = screening_result["image_quality"]

    if quality_result:
        print(f"- image_width: {quality_result['width']}")
        print(f"- image_height: {quality_result['height']}")
        print(f"- blur_score: {quality_result['blur_score']}")
        print(
            f"- is_low_resolution: "
            f"{quality_result['is_low_resolution']}"
        )
        print(f"- is_blurry: {quality_result['is_blurry']}")

    print("- flags:")

    if not screening_result["flags"]:
        print("  No document flags found.")

    for flag in screening_result["flags"]:
        print(f"  {flag['code']}: {flag['message']}")


def run_document_screening(image_file):
    image_path = Path(image_file)

    if not image_path.is_file():
        print(f"Image file not found: {image_path}")
        return

    # Full passport-image OCR for visible fields.
    ocr_result = read_image_text(image_path)

    print("\nOCR reader result:")
    print(f"- success: {ocr_result['success']}")
    print(
        f"- average_confidence: "
        f"{ocr_result['average_confidence']}"
    )
    print(f"- error: {ocr_result['error']}")

    if not ocr_result["success"]:
        return

    # Bottom-passport OCR for the MRZ only.
    mrz_ocr_result = read_mrz_text(image_path)

    print("\nMRZ OCR reader result:")
    print(f"- success: {mrz_ocr_result['success']}")
    print(
        f"- average_confidence: "
        f"{mrz_ocr_result['average_confidence']}"
    )
    print(f"- error: {mrz_ocr_result['error']}")

    passport_fields = extract_passport_fields(
        ocr_result["text_lines"]
    )

    mrz_result = extract_mrz(
        mrz_ocr_result["text_lines"]
        if mrz_ocr_result["success"]
        else []
    )

    # Safe debugging: prints only count and character lengths,
    # not the passport MRZ text itself.
    print("\nMRZ character check:")
    print(f"- MRZ lines found: {mrz_result['line_count']}")
    print(
        f"- Characters in each line: "
        f"{mrz_result['line_lengths']}"
    )
    print(
        f"- MRZ format valid: "
        f"{mrz_result['passport_mrz_format_valid']}"
    )

    screening_result = screen_document(
        passport_fields=passport_fields,
        mrz_result=mrz_result,
        average_confidence=ocr_result["average_confidence"],
        image_path=image_path,
    )

    print_screening_summary(screening_result)

    output_data = {
        "image_path": str(image_path),
        "ocr": ocr_result,
        "mrz_ocr": mrz_ocr_result,
        "passport_fields": passport_fields,
        "mrz": mrz_result,
        "screening": screening_result,
    }

    save_document_screening_result(output_data)


if __name__ == "__main__":
    arguments = parse_arguments()
    run_document_screening(arguments.image_path)