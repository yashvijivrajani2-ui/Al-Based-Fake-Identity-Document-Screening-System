import os
import re
import json
import datetime
import tkinter as tk
from tkinter import filedialog

import cv2
import pytesseract
from PIL import Image


# ============================================================
# 1. TESSERACT CONFIGURATION
# ============================================================

TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

if os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
else:
    print("WARNING: Tesseract was not found at:")
    print(TESSERACT_PATH)
    print("Please check your Tesseract installation path.")

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# 2. SELECT IMAGE
# ============================================================

def select_image():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select ID Document Image",
        filetypes=[
            ("Image files", "*.png *.jpg *.jpeg *.bmp *.webp"),
            ("All files", "*.*")
        ]
    )
    root.destroy()
    return file_path


# ============================================================
# 3. IMAGE PREPROCESSING
# ============================================================

def preprocess_image(image_path):

    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Could not open image:\n{image_path}")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    scale = 2
    enlarged = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    denoised = cv2.GaussianBlur(enlarged, (3, 3), 0)
    processed = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    cv2.imwrite(os.path.join(OUTPUT_DIR, "gray.png"), gray)
    cv2.imwrite(os.path.join(OUTPUT_DIR, "preprocessed.png"), processed)

    return processed


# ============================================================
# 4. GENERAL OCR
# ============================================================

def perform_ocr(processed_image):
    pil_image = Image.fromarray(processed_image)
    config = "--oem 3 --psm 6"
    return pytesseract.image_to_string(pil_image, config=config)


def clean_text(text):
    text = text.replace("\x0c", "")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)


# ============================================================
# 5. DOCUMENT TYPE CLASSIFICATION
# ============================================================

DOC_KEYWORDS = {
    "PASSPORT": ["PASSPORT", "PASAPORTE", "PASSEPORT", "PASSPOR"],
    "DRIVING_LICENSE": [
        "DRIVING LICENCE", "DRIVING LICENSE", "DRIVER LICENSE", "DRIVER'S LICENSE",
        "DL NO", "LICENCE NO", "LICENSE NO", "TRANSPORT DEPARTMENT", "MCWG", "LMV",
        "NON-TRANSPORT", "RTO"
    ],
    "AADHAAR": [
        "AADHAAR", "AADHAR", "UNIQUE IDENTIFICATION AUTHORITY", "UIDAI",
        "GOVERNMENT OF INDIA"
    ],
}


def classify_document(text):

    upper = text.upper()
    scores = {"PASSPORT": 0, "DRIVING_LICENSE": 0, "AADHAAR": 0}

    for doc_type, keywords in DOC_KEYWORDS.items():
        for kw in keywords:
            if kw in upper:
                scores[doc_type] += 1

    # A 12-digit number in 4-4-4 grouping is a strong Aadhaar signal
    if re.search(r"\b\d{4}\s?\d{4}\s?\d{4}\b", upper):
        scores["AADHAAR"] += 2

    # An MRZ-like line ("P<" followed by a 3-letter country code) is a
    # strong passport signal, even if the word PASSPORT itself was misread
    if re.search(r"P[A-Z<]?[A-Z]{3}", upper):
        scores["PASSPORT"] += 1

    best_type = max(scores, key=scores.get)
    if scores[best_type] == 0:
        return "UNKNOWN"
    return best_type


# ============================================================
# 6. COUNTRY CODES (used by MRZ + label detection)
# ============================================================

COUNTRY_CODES = {
    "IND": "India", "USA": "United States", "GBR": "United Kingdom",
    "CAN": "Canada", "AUS": "Australia", "DEU": "Germany", "FRA": "France",
    "ITA": "Italy", "ESP": "Spain", "PRT": "Portugal", "NLD": "Netherlands",
    "BEL": "Belgium", "CHE": "Switzerland", "AUT": "Austria", "JPN": "Japan",
    "CHN": "China", "KOR": "South Korea", "SGP": "Singapore", "MYS": "Malaysia",
    "THA": "Thailand", "ARE": "United Arab Emirates", "SAU": "Saudi Arabia",
    "QAT": "Qatar", "NZL": "New Zealand", "BRA": "Brazil", "MEX": "Mexico",
    "ZAF": "South Africa", "RUS": "Russia", "HTI": "Haiti",
}


def detect_country_from_labels(text):

    upper_text = text.upper()

    for pattern in [
        r"NATIONALITY\s*[:\-]?\s*([A-Z]+)",
        r"NATIONALITE\s*[:\-]?\s*([A-Z]+)",
        r"NACIONALIDAD\s*[:\-]?\s*([A-Z]+)"
    ]:
        match = re.search(pattern, upper_text)
        if match and match.group(1) in COUNTRY_CODES:
            return COUNTRY_CODES[match.group(1)]

    for code, country in COUNTRY_CODES.items():
        if re.search(r"\b" + code + r"\b", upper_text):
            return country

    for code, country in COUNTRY_CODES.items():
        if country.upper() in upper_text:
            return country

    return None


# ============================================================
# 7. MRZ HELPERS (passport-specific)
# ============================================================

def get_mrz_candidate_lines(text):
    candidates = []
    for line in text.upper().splitlines():
        cleaned = re.sub(r"[^A-Z0-9<]", "", line)
        if len(cleaned) >= 25 and cleaned.count("<") >= 2:
            candidates.append(cleaned)
    return candidates


def ocr_mrz_crop(gray_crop):
    pil_image = Image.fromarray(gray_crop)
    config = (
        "--oem 3 --psm 6 "
        "-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789<"
    )
    return pytesseract.image_to_string(pil_image, config=config)


def find_best_mrz(processed_image, general_text):
    """
    Tries several bottom-crop fractions instead of one fixed cut, since MRZ
    position varies with how the document was photographed/scanned. Falls
    back to scanning the general OCR text if no crop works.
    """
    height, width = processed_image.shape[:2]
    best_candidates = []
    best_text = ""
    best_crop = None

    for frac in (0.85, 0.75, 0.65, 0.55, 0.45, 0.30):
        crop_start = int(height * frac)
        crop = processed_image[crop_start:height, 0:width]
        if crop.shape[0] < 15:
            continue
        text = ocr_mrz_crop(crop)
        candidates = get_mrz_candidate_lines(text)
        if len(candidates) > len(best_candidates):
            best_candidates = candidates
            best_text = text
            best_crop = crop

    fallback_candidates = get_mrz_candidate_lines(general_text)
    if len(fallback_candidates) > len(best_candidates):
        best_candidates = fallback_candidates
        best_text = general_text

    if best_crop is not None:
        cv2.imwrite(os.path.join(OUTPUT_DIR, "mrz_crop.png"), best_crop)

    return best_text, best_candidates


def mrz_char_value(ch):
    if ch == "<":
        return 0
    if ch.isdigit():
        return int(ch)
    if ch.isalpha():
        return ord(ch) - ord("A") + 10
    return 0


def mrz_check_digit(data):
    weights = [7, 3, 1]
    total = sum(mrz_char_value(ch) * weights[i % 3] for i, ch in enumerate(data))
    return total % 10


def fix_ocr_digits(s):
    mapping = {"O": "0", "Q": "0", "D": "0", "I": "1", "L": "1",
               "Z": "2", "S": "5", "B": "8", "G": "6"}
    return "".join(mapping.get(c, c) for c in s)


def format_mrz_date(raw6):
    digits = fix_ocr_digits(raw6)
    if len(digits) != 6 or not digits.isdigit():
        return "Not detected"
    yy, mm, dd = digits[0:2], digits[2:4], digits[4:6]
    current_yy = int(str(datetime.date.today().year)[2:])
    century = "20" if int(yy) <= current_yy else "19"
    return f"{dd}/{mm}/{century}{yy}"


def parse_td3(line1, line2):
    line1 = (line1 + "<" * 44)[:44]
    line2 = (line2 + "<" * 44)[:44]

    issuing_country = line1[2:5]
    names_field = line1[5:44]
    surname, _, given = names_field.partition("<<")
    surname = surname.replace("<", " ").strip()
    given = given.replace("<", " ").strip()

    passport_number_raw = line2[0:9]
    passport_check = line2[9]
    nationality_code = line2[10:13]
    dob_raw = line2[13:19]
    dob_check = line2[19]
    sex_char = line2[20]
    expiry_raw = line2[21:27]
    expiry_check = line2[27]

    def check_ok(data, check_char):
        return bool(check_char.isdigit() and mrz_check_digit(data) == int(check_char))

    return {
        "mrz_format": "TD3",
        "issuing_country": COUNTRY_CODES.get(issuing_country, issuing_country),
        "nationality": COUNTRY_CODES.get(nationality_code, nationality_code),
        "surname": surname or "Not detected",
        "given_names": given or "Not detected",
        "passport_number": passport_number_raw.replace("<", "").strip() or "Not detected",
        "passport_number_check_valid": check_ok(passport_number_raw, passport_check),
        "date_of_birth": format_mrz_date(dob_raw),
        "date_of_birth_check_valid": check_ok(fix_ocr_digits(dob_raw), dob_check),
        "sex": sex_char if sex_char in ("M", "F") else "Not detected",
        "expiry_date": format_mrz_date(expiry_raw),
        "expiry_date_check_valid": check_ok(fix_ocr_digits(expiry_raw), expiry_check),
    }


def parse_td1(line1, line2, line3):
    line1 = (line1 + "<" * 30)[:30]
    line2 = (line2 + "<" * 30)[:30]
    line3 = (line3 + "<" * 30)[:30]

    issuing_country = line1[2:5]
    document_number_raw = line1[5:14]
    document_check = line1[14]

    dob_raw = line2[0:6]
    dob_check = line2[6]
    sex_char = line2[7]
    expiry_raw = line2[8:14]
    expiry_check = line2[14]
    nationality_code = line2[15:18]

    surname, _, given = line3.partition("<<")
    surname = surname.replace("<", " ").strip()
    given = given.replace("<", " ").strip()

    def check_ok(data, check_char):
        return bool(check_char.isdigit() and mrz_check_digit(data) == int(check_char))

    return {
        "mrz_format": "TD1",
        "issuing_country": COUNTRY_CODES.get(issuing_country, issuing_country),
        "nationality": COUNTRY_CODES.get(nationality_code, nationality_code),
        "surname": surname or "Not detected",
        "given_names": given or "Not detected",
        "passport_number": document_number_raw.replace("<", "").strip() or "Not detected",
        "passport_number_check_valid": check_ok(document_number_raw, document_check),
        "date_of_birth": format_mrz_date(dob_raw),
        "date_of_birth_check_valid": check_ok(fix_ocr_digits(dob_raw), dob_check),
        "sex": sex_char if sex_char in ("M", "F") else "Not detected",
        "expiry_date": format_mrz_date(expiry_raw),
        "expiry_date_check_valid": check_ok(fix_ocr_digits(expiry_raw), expiry_check),
    }


def parse_mrz(candidate_lines):
    if not candidate_lines:
        return None

    td3_lines = [l for l in candidate_lines if 38 <= len(l) <= 48]
    if len(td3_lines) >= 2:
        result = parse_td3(td3_lines[-2], td3_lines[-1])
        if result["passport_number"] != "Not detected":
            return result

    td1_lines = [l for l in candidate_lines if 25 <= len(l) <= 34]
    if len(td1_lines) >= 3:
        result = parse_td1(td1_lines[-3], td1_lines[-2], td1_lines[-1])
        if result["passport_number"] != "Not detected":
            return result

    return None


# ============================================================
# 8. PASSPORT EXTRACTOR
# ============================================================

def extract_passport(general_text, processed_image):

    mrz_text, mrz_candidates = find_best_mrz(processed_image, general_text)
    mrz_result = parse_mrz(mrz_candidates)
    label_country = detect_country_from_labels(general_text)

    if mrz_result:
        details = dict(mrz_result)
        details["country_detected"] = mrz_result["issuing_country"]
    else:
        details = {
            "mrz_format": "Not detected",
            "country_detected": label_country or "Not detected",
            "nationality": label_country or "Not detected",
            "surname": "Not detected",
            "given_names": "Not detected",
            "passport_number": "Not detected",
            "passport_number_check_valid": False,
            "date_of_birth": "Not detected",
            "date_of_birth_check_valid": False,
            "expiry_date": "Not detected",
            "expiry_date_check_valid": False,
            "sex": "Not detected",
        }

    details["mrz_detected"] = mrz_candidates
    return details


# ============================================================
# 9. AADHAAR EXTRACTOR
# ============================================================

def extract_aadhaar(text):

    upper = text.upper()

    aadhaar_match = re.search(r"\b(\d{4}\s?\d{4}\s?\d{4})\b", text)
    aadhaar_number = re.sub(r"\s", "", aadhaar_match.group(1)) if aadhaar_match else "Not detected"

    dob_match = re.search(
        r"(?:DOB|DATE OF BIRTH|YEAR OF BIRTH)\s*[:\-]?\s*(\d{2}[\/\-]\d{2}[\/\-]\d{4}|\d{4})",
        upper
    )
    dob = dob_match.group(1) if dob_match else "Not detected"

    gender_match = re.search(r"\b(MALE|FEMALE|TRANSGENDER)\b", upper)
    gender = gender_match.group(1).title() if gender_match else "Not detected"

    return {
        "country_detected": "India",
        "aadhaar_number": aadhaar_number,
        "date_of_birth": dob,
        "gender": gender,
    }


# ============================================================
# 10. DRIVING LICENSE EXTRACTOR
# ============================================================

def extract_driving_license(text):

    upper = text.upper()

    dl_match = re.search(
        r"(?:DL\s*NO\.?|LICEN[CS]E\s*NO\.?)\s*[:\-]?\s*([A-Z0-9][A-Z0-9\-\/ ]{4,20}[A-Z0-9])",
        upper
    )
    license_number = dl_match.group(1).strip() if dl_match else "Not detected"

    dob_match = re.search(r"(?:DOB|DATE OF BIRTH)\s*[:\-]?\s*(\d{2}[\/\-]\d{2}[\/\-]\d{4})", upper)
    dob = dob_match.group(1) if dob_match else "Not detected"

    validity_match = re.search(
        r"(?:VALID\s*(?:TILL|UPTO|THRU)?|VALIDITY)\s*[:\-]?\s*(\d{2}[\/\-]\d{2}[\/\-]\d{4})",
        upper
    )
    valid_till = validity_match.group(1) if validity_match else "Not detected"

    blood_group_match = re.search(r"\b(A|B|AB|O|0)\s?[+-](?:VE)?", upper)
    blood_group = blood_group_match.group(0) if blood_group_match else "Not detected"

    country_detected = detect_country_from_labels(text) or "Not detected"

    return {
        "country_detected": country_detected,
        "license_number": license_number,
        "date_of_birth": dob,
        "valid_till": valid_till,
        "blood_group": blood_group,
    }


# ============================================================
# 11. DISPATCH / BUILD RESULT
# ============================================================

def extract_document_details(general_text, processed_image):

    doc_type = classify_document(general_text)

    if doc_type == "PASSPORT":
        details = extract_passport(general_text, processed_image)
    elif doc_type == "AADHAAR":
        details = extract_aadhaar(general_text)
    elif doc_type == "DRIVING_LICENSE":
        details = extract_driving_license(general_text)
    else:
        details = {"country_detected": detect_country_from_labels(general_text) or "Not detected"}

    result = {
        "document_type_detected": doc_type,
        "details": details,
        "ocr_text": general_text,
    }

    return result


# ============================================================
# 12. SAVE / DISPLAY
# ============================================================

def save_json(result):
    json_path = os.path.join(OUTPUT_DIR, "result.json")
    with open(json_path, "w", encoding="utf-8") as file:
        json.dump(result, file, indent=4, ensure_ascii=False)
    return json_path


def display_result(result):
    print("\n" + "=" * 60)
    print("              DOCUMENT OCR RESULT")
    print("=" * 60)
    print("Document Type Detected :", result["document_type_detected"])

    for key, value in result["details"].items():
        if key == "mrz_detected":
            continue
        print(f"{key:28}:", value)

    print("=" * 60)
    print("\nJSON file created successfully.")


# ============================================================
# 13. MAIN
# ============================================================

def main():

    print("=" * 60)
    print("     MULTI-DOCUMENT OCR SYSTEM (Passport / DL / Aadhaar)")
    print("=" * 60)

    image_path = select_image()
    if not image_path:
        print("\nNo image selected.")
        return

    print("\nSelected image:")
    print(image_path)

    try:
        processed_image = preprocess_image(image_path)

        print("\nRunning OCR...")
        raw_text = perform_ocr(processed_image)

        if not raw_text.strip():
            print("\nNo text detected. Try a clearer image.")
            return

        text = clean_text(raw_text)

        print("\n" + "=" * 60)
        print("                    OCR TEXT")
        print("=" * 60)
        print(text)

        result = extract_document_details(text, processed_image)

        json_path = save_json(result)
        display_result(result)

        print("\nJSON saved at:")
        print(os.path.abspath(json_path))

    except Exception as error:
        print("\n" + "=" * 60)
        print("ERROR")
        print("=" * 60)
        print(type(error).__name__)
        print(error)


if __name__ == "__main__":
    main()