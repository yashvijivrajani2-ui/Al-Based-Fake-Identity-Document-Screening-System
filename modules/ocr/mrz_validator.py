MRZ_WEIGHTS = [7, 3, 1]


def _character_value(character):
    if character.isdigit():
        return int(character)

    if "A" <= character <= "Z":
        return ord(character) - ord("A") + 10

    if character == "<":
        return 0

    raise ValueError(f"Invalid MRZ character: {character}")


def calculate_check_digit(value):
    total = 0

    for index, character in enumerate(value):
        total += _character_value(character) * MRZ_WEIGHTS[index % 3]

    return str(total % 10)


def validate_passport_mrz(mrz_result):
    if not mrz_result["passport_mrz_format_valid"]:
        return {
            "checksum_validation_available": False,
            "checksum_valid": False,
            "checks": {},
            "error": "MRZ format must contain two lines of 44 characters."
        }

    line_one, line_two = mrz_result["mrz_lines"]

    document_number = line_two[0:9]
    document_number_check = line_two[9]

    birth_date = line_two[13:19]
    birth_date_check = line_two[19]

    expiry_date = line_two[21:27]
    expiry_date_check = line_two[27]

    personal_number = line_two[28:42]
    personal_number_check = line_two[42]

    composite_value = (
        line_two[0:10]
        + line_two[13:20]
        + line_two[21:43]
    )
    composite_check = line_two[43]

    checks = {
        "document_number": (
            calculate_check_digit(document_number)
            == document_number_check
        ),
        "birth_date": (
            calculate_check_digit(birth_date)
            == birth_date_check
        ),
        "expiry_date": (
            calculate_check_digit(expiry_date)
            == expiry_date_check
        ),
        "personal_number": (
            calculate_check_digit(personal_number)
            == personal_number_check
        ),
        "composite": (
            calculate_check_digit(composite_value)
            == composite_check
        ),
    }

    return {
        "checksum_validation_available": True,
        "checksum_valid": all(checks.values()),
        "checks": checks,
        "error": None
    }