from pathlib import Path

from modules.ocr.image_ocr_reader import read_image_text
from modules.ocr.mrz_extractor import extract_mrz
from modules.ocr.mrz_validator import validate_passport_mrz


PROJECT_ROOT = Path(__file__).resolve().parents[2]

IMAGE_FILE = (
    PROJECT_ROOT
    / "datasets"
    / "sample_documents"
    / "passports"
    / "synthetic_valid_01.png"
)


def run_mrz_validation_test():
    ocr_result = read_image_text(IMAGE_FILE)

    if not ocr_result["success"]:
        print(f"OCR failed: {ocr_result['error']}")
        return

    mrz_result = extract_mrz(ocr_result["text_lines"])
    validation_result = validate_passport_mrz(mrz_result)

    print("\nMRZ checksum validation result:")
    print(
        f"- checksum_validation_available: "
        f"{validation_result['checksum_validation_available']}"
    )
    print(f"- checksum_valid: {validation_result['checksum_valid']}")
    print(f"- error: {validation_result['error']}")

    print("- individual checks:")

    for check_name, check_passed in validation_result["checks"].items():
        print(f"  {check_name}: {check_passed}")


if __name__ == "__main__":
    run_mrz_validation_test()