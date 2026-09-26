REQUIRED_FIELDS = [
    "full_name",
    "passport_number",
    "nationality",
    "date_of_birth",
    "gender",
    "issue_date",
    "expiry_date"
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