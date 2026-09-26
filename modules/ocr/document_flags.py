REQUIRED_FIELDS = [
    "full_name",
    "passport_number",
    "nationality",
    "date_of_birth",
    "gender",
    "issue_date",
    "expiry_date",
]


def build_document_flags(passport_fields, mrz_result, average_confidence):
    flags = []

    missing_fields = [
        field_name
        for field_name in REQUIRED_FIELDS
        if not passport_fields.get(field_name)
    ]

    if missing_fields:
        flags.append({
            "code": "MISSING_REQUIRED_FIELDS",
            "message": (
                "Required fields are missing: "
                + ", ".join(missing_fields)
            )
        })

    if average_confidence < 0.85:
        flags.append({
            "code": "LOW_OCR_CONFIDENCE",
            "message": (
                f"Average OCR confidence is low: "
                f"{average_confidence}"
            )
        })

    if not mrz_result["mrz_present"]:
        flags.append({
            "code": "MRZ_NOT_FOUND",
            "message": "Two MRZ lines could not be detected."
        })

    elif not mrz_result["passport_mrz_format_valid"]:
        flags.append({
            "code": "MRZ_FORMAT_INVALID",
            "message": (
                "Passport MRZ must contain two lines "
                "with exactly 44 characters each."
            )
        })

    return {
        "review_required": len(flags) > 0,
        "flag_count": len(flags),
        "flags": flags
    }