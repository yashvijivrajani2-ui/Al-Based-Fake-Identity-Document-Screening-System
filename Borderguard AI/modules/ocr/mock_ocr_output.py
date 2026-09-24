MOCK_PASSPORT_OCR = {
    "document_type": "Passport",
    "country_code": "TST",
    "passport_number": "TEST123456",
    "surname": "SAMPLE",
    "given_names": "TEST USER",
    "nationality": "Test Nationality",
    "date_of_birth": "1995-01-01",
    "sex": "X",
    "date_of_expiry": "2030-01-01",
    "source": "synthetic_test_data"
}


def get_mock_passport_ocr():
    return MOCK_PASSPORT_OCR.copy()


if __name__ == "__main__":
    extracted_data = get_mock_passport_ocr()

    print("Mock OCR result:")
    for field, value in extracted_data.items():
        print(f"{field}: {value}")
        