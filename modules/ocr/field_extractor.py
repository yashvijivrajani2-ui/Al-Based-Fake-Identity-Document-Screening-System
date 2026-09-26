import re


def _clean_value(value):
    if not value:
        return None

    value = re.sub(r"\s+", " ", str(value)).strip(" :.-")

    if not value:
        return None

    return value.upper()


def _find_value(text_lines, labels):
    for index, line in enumerate(text_lines):
        line = str(line).strip()

        for label in labels:
            pattern = rf"^\s*(?:{label})\s*[:\-]?\s*(.*)$"
            match = re.search(pattern, line, flags=re.IGNORECASE)

            if not match:
                continue

            same_line_value = match.group(1).strip()

            # Ignore bilingual label text such as:
            # "NAME / NOM / PRENOMS"
            # "PASSPORT NO / N° DE PASSEPORT"
            if same_line_value and not same_line_value.startswith("/"):
                return _clean_value(same_line_value)

            # Passport value is often on the next OCR line
            if index + 1 < len(text_lines):
                next_line = str(text_lines[index + 1]).strip()

                if next_line:
                    return _clean_value(next_line)

    return None


def extract_passport_fields(text_lines):
    surname = _find_value(
        text_lines,
        [
            r"Surname",
            r"Last\s+Name",
            r"Family\s+Name",
            r"Nom",
        ],
    )

    given_names = _find_value(
        text_lines,
        [
            r"Given\s+Name(?:s)?",
            r"First\s+Name",
            r"Forename(?:s)?",
            r"Pr[ée]nom(?:s)?",
        ],
    )

    full_name = _find_value(
        text_lines,
        [
            r"Full\s+Name",
            r"Name",
            r"Nom\s*/\s*Pr[ée]nom(?:s)?",
        ],
    )

    # If the passport has surname and given names separately,
    # combine them to create full_name.
    if not full_name:
        name_parts = [part for part in [surname, given_names] if part]
        full_name = " ".join(name_parts) if name_parts else None

    fields = {
        "full_name": full_name,

        "passport_number": _find_value(
            text_lines,
            [
                r"Passport\s+(?:Number|No\.?)",
                r"Document\s+(?:Number|No\.?)",
                r"Passport\s+Code",
                r"N[°ºo]\s*de\s*Passeport",
                r"Num[ée]ro\s*de\s*Passeport",
            ],
        ),

        "nationality": _find_value(
            text_lines,
            [
                r"Nationality",
                r"Nationalit[ée]",
                r"Country\s+Code",
            ],
        ),

        "date_of_birth": _find_value(
            text_lines,
            [
                r"Date\s+of\s+Birth",
                r"Birth\s+Date",
                r"Date\s+de\s+Naissance",
            ],
        ),

        "gender": _find_value(
            text_lines,
            [
                r"Gender",
                r"Sex",
                r"Sexe",
            ],
        ),

        "issue_date": _find_value(
            text_lines,
            [
                r"Issue\s+Date",
                r"Date\s+of\s+Issue",
                r"Date\s+Issued",
                r"Date\s+de\s+D[ée]livrance",
            ],
        ),

        "expiry_date": _find_value(
            text_lines,
            [
                r"Expiry\s+Date",
                r"Expiration\s+Date",
                r"Date\s+of\s+Expiry",
                r"Date\s+of\s+Expiration",
                r"Valid\s+Until",
                r"Date\s+d['’]Expiration",
            ],
        ),
    }

    return fields