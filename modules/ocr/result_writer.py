import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_FOLDER = PROJECT_ROOT / "outputs" / "ocr_results"


def json_default(value):
    if isinstance(value, Path):
        return str(value)

    if hasattr(value, "item"):
        return value.item()

    raise TypeError(
        f"Object of type {type(value).__name__} "
        "is not JSON serializable"
    )


def save_json_result(output_data, filename):
    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

    output_file = OUTPUT_FOLDER / filename

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(
            output_data,
            file,
            indent=4,
            default=json_default
        )

    print(f"\nJSON result saved to: {output_file}")

    return output_file


def save_ocr_result(ocr_data, validation_result):
    output_data = {
        "ocr_data": ocr_data,
        "validation": validation_result,
    }

    return save_json_result(
        output_data=output_data,
        filename="mock_ocr_result.json"
    )


def save_document_screening_result(screening_result):
    return save_json_result(
        output_data=screening_result,
        filename="document_screening_result.json"
    )