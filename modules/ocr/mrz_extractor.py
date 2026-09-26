import re


def _clean_mrz_line(text):
    text = str(text).upper()

    # Convert OCR angle-bracket variations into the MRZ separator.
    text = text.replace("«", "<")
    text = text.replace("‹", "<")
    text = text.replace("〈", "<")

    # Remove spaces and characters that cannot occur in MRZ.
    return re.sub(r"[^A-Z0-9<]", "", text)


def _is_mrz_fragment(text):
    cleaned = _clean_mrz_line(text)

    # A fragment must contain an MRZ separator and enough characters.
    return "<" in cleaned and len(cleaned) >= 8


def _split_long_mrz_line(line):
    if len(line) == 88:
        return [line[:44], line[44:]]

    return [line]


def _find_mrz_candidates(text_lines):
    fragments = []

    for line in text_lines:
        if _is_mrz_fragment(line):
            cleaned = _clean_mrz_line(line)
            fragments.extend(_split_long_mrz_line(cleaned))

    candidates = []

    # Keep complete or nearly complete MRZ lines.
    for fragment in fragments:
        if 30 <= len(fragment) <= 50:
            candidates.append(fragment)

    # OCR may split one MRZ line into two or more pieces.
    for start_index in range(len(fragments)):
        combined = ""

        for end_index in range(start_index, min(start_index + 4, len(fragments))):
            combined += fragments[end_index]

            if 30 <= len(combined) <= 50:
                candidates.append(combined)

            if len(combined) > 50:
                break

    # Remove duplicates while preserving order.
    unique_candidates = []

    for candidate in candidates:
        if candidate not in unique_candidates:
            unique_candidates.append(candidate)

    return unique_candidates


def _choose_mrz_lines(candidates):
    exact_lines = [line for line in candidates if len(line) == 44]

    # Standard passport MRZ is two lines, each 44 characters.
    if len(exact_lines) >= 2:
        return exact_lines[-2:]

    # If OCR missed a few characters, retain the two best near-44 lines
    # but mark format validation as false.
    near_lines = [
        line
        for line in candidates
        if 30 <= len(line) <= 50
    ]

    near_lines.sort(key=lambda line: abs(len(line) - 44))

    if len(near_lines) >= 2:
        return near_lines[:2]

    return []


def extract_mrz(text_lines):
    candidates = _find_mrz_candidates(text_lines)
    mrz_lines = _choose_mrz_lines(candidates)

    line_lengths = [len(line) for line in mrz_lines]

    return {
        "mrz_present": len(mrz_lines) == 2,
        "mrz_lines": mrz_lines,
        "mrz_text": "\n".join(mrz_lines),
        "line_count": len(mrz_lines),
        "line_lengths": line_lengths,
        "passport_mrz_format_valid": (
            len(mrz_lines) == 2
            and all(length == 44 for length in line_lengths)
        ),
    }