import re


def _normalize_passport_number(value):
    if not value:
        return None

    return re.sub(r"[^A-Z0-9]", "", value.upper())


def _normalize_date_to_mrz(value):
    if not value:
        return None

    digits = re.sub(r"[^0-9]", "", value)

    if len(digits) == 8:
        return digits[2:4] + digits[4:6] + digits[6:8]

    return None


def _normalize_gender(value):
    if not value:
        return None

    return value.upper()[0]


def compare_visible_fields_with_mrz(passport_fields, mrz_result):
    if not mrz_result["passport_mrz_format_valid"]:
        return {
            "comparison_available": False,
            "fields_match": False,
            "comparisons": {},
            "mismatches": [],
            "error": "MRZ must contain two lines of 44 characters."
        }

    line_two = mrz_result["mrz_lines"][1]

    mrz_fields = {
        "passport_number": line_two[0:9],
        "nationality": line_two[10:13],
        "date_of_birth": line_two[13:19],
        "gender": line_two[20],
        "expiry_date": line_two[21:27],
    }

    visible_fields = {
        "passport_number": _normalize_passport_number(
            passport_fields.get("passport_number")
        ),
        "nationality": (
            passport_fields.get("nationality", "").upper()
            if passport_fields.get("nationality")
            else None
        ),
        "date_of_birth": _normalize_date_to_mrz(
            passport_fields.get("date_of_birth")
        ),
        "gender": _normalize_gender(
            passport_fields.get("gender")
        ),
        "expiry_date": _normalize_date_to_mrz(
            passport_fields.get("expiry_date")
        ),
    }

    comparisons = {}
    mismatches = []

    for field_name, visible_value in visible_fields.items():
        mrz_value = mrz_fields[field_name]

        matches = (
            visible_value is not None
            and visible_value == mrz_value
        )

        comparisons[field_name] = {
            "visible_value": visible_value,
            "mrz_value": mrz_value,
            "matches": matches
        }

        if not matches:
            mismatches.append(field_name)

    return {
        "comparison_available": True,
        "fields_match": len(mismatches) == 0,
        "comparisons": comparisons,
        "mismatches": mismatches,
        "error": None
    }