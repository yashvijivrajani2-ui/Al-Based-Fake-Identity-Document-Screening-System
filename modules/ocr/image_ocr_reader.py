import os
from pathlib import Path

import cv2
import numpy as np
from paddleocr import PaddleOCR


os.environ["PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT"] = "0"
os.environ["FLAGS_use_mkldnn"] = "0"


def _empty_result(error_message):
    return {
        "success": False,
        "raw_text": "",
        "text_lines": [],
        "average_confidence": 0.0,
        "error": error_message,
    }


def _run_ocr(ocr_input):
    try:
        ocr = PaddleOCR(
            lang="en",
            enable_mkldnn=False,
        )

        results = ocr.predict(ocr_input)

        if not results:
            return _empty_result("OCR returned no result")

        first_result = results[0]
        text_lines = list(first_result["rec_texts"])
        confidence_scores = list(first_result["rec_scores"])

        average_confidence = (
            sum(confidence_scores) / len(confidence_scores)
            if confidence_scores
            else 0.0
        )

        return {
            "success": True,
            "raw_text": "\n".join(text_lines),
            "text_lines": text_lines,
            "average_confidence": round(float(average_confidence), 4),
            "error": None,
        }

    except Exception as error:
        return _empty_result(str(error))


def read_image_text(image_path):
    image_file = Path(image_path)

    if not image_file.exists():
        return _empty_result(f"Image file not found: {image_file}")

    return _run_ocr(str(image_file))


def read_mrz_text(image_path):
    image_file = Path(image_path)

    if not image_file.exists():
        return _empty_result(f"Image file not found: {image_file}")

    image = cv2.imread(str(image_file))

    if image is None:
        return _empty_result("Could not open image for MRZ OCR")

    height, width = image.shape[:2]

    # The machine-readable zone is normally in the lower part of
    # a passport identity page.
    mrz_crop = image[int(height * 0.58):height, 0:width]

    # Enlarge small MRZ characters before OCR.
    mrz_crop = cv2.resize(
        mrz_crop,
        None,
        fx=3,
        fy=3,
        interpolation=cv2.INTER_CUBIC,
    )

    gray = cv2.cvtColor(mrz_crop, cv2.COLOR_BGR2GRAY)

    # Improve local contrast so small MRZ characters are clearer.
    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8),
    )
    enhanced = clahe.apply(gray)

    # Convert back to three channels because OCR expects an image.
    prepared_mrz = cv2.cvtColor(
        enhanced,
        cv2.COLOR_GRAY2BGR,
    )

    return _run_ocr(prepared_mrz)