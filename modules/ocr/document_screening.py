from modules.ocr.document_flags import build_document_flags
from modules.ocr.field_mrz_comparison import compare_visible_fields_with_mrz
from modules.ocr.image_quality import assess_image_quality
from modules.ocr.mrz_validator import validate_passport_mrz


def screen_document(
    passport_fields,
    mrz_result,
    average_confidence,
    image_path=None
):
    screening_result = build_document_flags(
        passport_fields=passport_fields,
        mrz_result=mrz_result,
        average_confidence=average_confidence
    )

    checksum_result = validate_passport_mrz(mrz_result)

    comparison_result = compare_visible_fields_with_mrz(
        passport_fields,
        mrz_result
    )

    quality_result = None

    if image_path:
        quality_result = assess_image_quality(image_path)

        if quality_result["quality_check_available"]:
            if quality_result["is_low_resolution"]:
                screening_result["flags"].append({
                    "code": "LOW_RESOLUTION",
                    "message": (
                        "Image resolution is below the minimum "
                        "screening threshold."
                    )
                })

            if quality_result["is_blurry"]:
                screening_result["flags"].append({
                    "code": "BLURRY_IMAGE",
                    "message": (
                        "Image blur is above the allowed "
                        "screening threshold."
                    )
                })

            if quality_result["is_too_dark"]:
                screening_result["flags"].append({
                    "code": "IMAGE_TOO_DARK",
                    "message": (
                        "Image brightness is below the allowed "
                        "screening threshold."
                    )
                })

            if quality_result["is_too_bright"]:
                screening_result["flags"].append({
                    "code": "IMAGE_TOO_BRIGHT",
                    "message": (
                        "Image brightness is above the allowed "
                        "screening threshold."
                    )
                })

            if quality_result["is_wrong_orientation"]:
                screening_result["flags"].append({
                    "code": "WRONG_ORIENTATION",
                    "message": (
                        "Passport image is portrait-oriented and "
                        "should be recaptured in landscape orientation."
                    )
                })

            if quality_result["is_cropped"]:
                screening_result["flags"].append({
                    "code": "CROPPED_DOCUMENT",
                    "message": (
                        "Passport image aspect ratio suggests that "
                        "the document may be cropped."
                    )
                })

            if quality_result["is_glare_detected"]:
                screening_result["flags"].append({
                    "code": "GLARE_DETECTED",
                    "message": (
                        "Passport image glare may be obscuring the "
                        "MRZ or other critical document details."
                    )
                })

    if (
        checksum_result["checksum_validation_available"]
        and not checksum_result["checksum_valid"]
    ):
        screening_result["flags"].append({
            "code": "MRZ_CHECKSUM_INVALID",
            "message": (
                "One or more passport MRZ check digits are invalid."
            )
        })

    if (
        comparison_result["comparison_available"]
        and not comparison_result["fields_match"]
    ):
        mismatched_fields = ", ".join(
            comparison_result["mismatches"]
        )

        screening_result["flags"].append({
            "code": "VISIBLE_MRZ_MISMATCH",
            "message": (
                "Visible passport fields do not match MRZ fields: "
                + mismatched_fields
            )
        })

    screening_result["mrz_checksum"] = checksum_result

    screening_result["field_mrz_comparison"] = comparison_result

    screening_result["image_quality"] = quality_result

    screening_result["flag_count"] = len(
        screening_result["flags"]
    )

    screening_result["review_required"] = (
        screening_result["flag_count"] > 0
    )

    return screening_result