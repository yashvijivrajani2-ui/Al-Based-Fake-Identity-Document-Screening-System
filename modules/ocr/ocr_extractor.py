from pathlib import Path

from modules.ocr.mock_ocr_output import get_mock_passport_ocr
from modules.ocr.ocr_validator import validate_ocr_result
from modules.ocr.result_writer import save_ocr_result

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PASSPORTS_FOLDER = PROJECT_ROOT / "datasets" / "sample_documents" / "passports"


def find_sample_documents():
    print("OCR extractor started")
    print(f"Checking folder: {PASSPORTS_FOLDER}")

    if not PASSPORTS_FOLDER.exists():
        print("Folder not found")
        return []

    allowed_extensions = {".jpg", ".jpeg", ".png", ".webp"}

    documents = [
        file
        for file in PASSPORTS_FOLDER.iterdir()
        if file.is_file() and file.suffix.lower() in allowed_extensions
    ]

    print("Folder checker working")
    print(f"Images found: {len(documents)}")

    return documents


def run_mock_ocr():
    mock_data = get_mock_passport_ocr()

    print("\nSynthetic mock OCR result:")

    for field, value in mock_data.items():
        print(f"{field}: {value}")

    return mock_data


def display_validation_result(ocr_data):
    validation = validate_ocr_result(ocr_data)

    print("\nValidation result:")

    if validation["is_valid"]:
        print("Status: VALID")
        print("All required synthetic OCR fields are present.")
    else:
        print("Status: INVALID")
        print("Missing fields:")

        for field in validation["missing_fields"]:
            print(f"- {field}")

    return validation


if __name__ == "__main__":
    find_sample_documents()

    ocr_data = run_mock_ocr()
    validation_result = display_validation_result(ocr_data)

    save_ocr_result(ocr_data, validation_result)
    