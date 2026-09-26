from pathlib import Path

from modules.ocr.document_screening import screen_document
from modules.ocr.field_extractor import extract_passport_fields
from modules.ocr.image_ocr_reader import read_image_text
from modules.ocr.mrz_extractor import extract_mrz


PROJECT_ROOT = Path(__file__).resolve().parents[2]

IMAGE_FILE = (
    PROJECT_ROOT
    / "datasets"
    / "sample_documents"
    / "passports"
    / "synthetic_mismatch_01.png"
)


def run_document_screening_test():
    ocr_result = read_image_text(IMAGE_FILE)

    if not ocr_result["success"]:
        print(f"OCR failed: {ocr_result['error']}")
        return

    passport_fields = extract_passport_fields(ocr_result["text_lines"])
    mrz_result = extract_mrz(ocr_result["text_lines"])

    screening_result = screen_document(
        passport_fields=passport_fields,
        mrz_result=mrz_result,
        average_confidence=ocr_result["average_confidence"]
    )

    print("\nFull document screening result:")
    print(f"- review_required: {screening_result['review_required']}")
    print(f"- flag_count: {screening_result['flag_count']}")
    print(
        f"- mrz_checksum_valid: "
        f"{screening_result['mrz_checksum']['checksum_valid']}"
    )

    print("- flags:")

    if not screening_result["flags"]:
        print("  No document flags found.")

    for flag in screening_result["flags"]:
        print(f"  {flag['code']}: {flag['message']}")


if __name__ == "__main__":
    run_document_screening_test()
