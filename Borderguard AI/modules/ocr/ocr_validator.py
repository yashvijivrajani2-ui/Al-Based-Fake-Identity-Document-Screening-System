REQUIRED_FIELDS = [
    "document_type",
    "country_code",
    "passport_number",
    "surname",
    "given_names",
    "nationality",
    "date_of_birth",
    "date_of_expiry",
]


def validate_ocr_result(ocr_data):
    missing_fields = []

    for field in REQUIRED_FIELDS:
        value = ocr_data.get(field)

        if value is None or str(value).strip() == "":
            missing_fields.append(field)

    is_valid = len(missing_fields) == 0

    return {
        "is_valid": is_valid,
        "missing_fields": missing_fields,
        "checked_fields": REQUIRED_FIELDS,
    }