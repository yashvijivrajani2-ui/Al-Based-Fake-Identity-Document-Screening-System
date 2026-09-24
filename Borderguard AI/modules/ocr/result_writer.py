import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_FOLDER = PROJECT_ROOT / "outputs" / "ocr_results"


def save_ocr_result(ocr_data, validation_result):
    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

    output_data = {
        "ocr_data": ocr_data,
        "validation": validation_result,
    }

    output_file = OUTPUT_FOLDER / "mock_ocr_result.json"

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(output_data, file, indent=4)

    print(f"\nJSON result saved to: {output_file}")

    return output_file