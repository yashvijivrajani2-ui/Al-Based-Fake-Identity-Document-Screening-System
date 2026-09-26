from pathlib import Path

from modules.ocr.field_extractor import extract_passport_fields
from modules.ocr.field_mrz_comparison import compare_visible_fields_with_mrz
from modules.ocr.image_ocr_reader import read_image_text
from modules.ocr.mrz_extractor import extract_mrz


PROJECT_ROOT = Path(__file__).resolve().parents[2]

IMAGE_FILE = (
    PROJECT_ROOT
    / "datasets"
    / "sample_documents"
    / "passports"
    / "synthetic_valid_01.png"
)


def run_field_mrz_comparison_test():
    ocr_result = read_image_text(IMAGE_FILE)

    if not ocr_result["success"]:
        print(f"OCR failed: {ocr_result['error']}")
        return

    passport_fields = extract_passport_fields(ocr_result["text_lines"])
    mrz_result = extract_mrz(ocr_result["text_lines"])

    comparison_result = compare_visible_fields_with_mrz(
        passport_fields,
        mrz_result
    )

    print("\nVisible-field versus MRZ comparison:")
    print(
        f"- comparison_available: "
        f"{comparison_result['comparison_available']}"
    )
    print(f"- fields_match: {comparison_result['fields_match']}")
    print(f"- mismatches: {comparison_result['mismatches']}")
    print(f"- error: {comparison_result['error']}")

    print("- individual comparisons:")

    for field_name, comparison in comparison_result["comparisons"].items():
        print(
            f"  {field_name}: "
            f"visible={comparison['visible_value']}, "
            f"mrz={comparison['mrz_value']}, "
            f"matches={comparison['matches']}"
        )


if __name__ == "__main__":
    run_field_mrz_comparison_test()