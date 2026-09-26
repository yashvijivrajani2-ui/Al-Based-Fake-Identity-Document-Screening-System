def get_mock_passport_ocr():
    return {
        "contract_version": "1.0.0",
        "document_id": "DOC-2026-00001",
        "ocr_status": "success",
        "ocr_confidence": 0.92,
        "full_name": "SAMPLE TRAVELER",
        "passport_number": "A12345678",
        "nationality": "IND",
        "date_of_birth": "2002-08-12",
        "gender": "F",
        "issue_date": "2022-05-10",
        "expiry_date": "2032-05-10",
        "mrz_text_raw": [
            "P<INDSAMPLE<<TRAVELER<<<<<<<<<<<<<<<<<<<<<<",
            "A123456784IND0208127F3205105<<<<<<<<<<<<<<08"
        ],
        "mrz_text_cleaned": [
            "P<INDSAMPLE<<TRAVELER<<<<<<<<<<<<<<<<<<<<<<",
            "A123456784IND0208127F3205105<<<<<<<<<<<<<<08"
        ],
        "mrz_confidence": 0.89,
        "quality_flags": {
            "blur": False,
            "glare": False,
            "cropped": False,
            "low_resolution": False,
            "wrong_orientation": False,
            "mrz_visible": True
        },
        "document_flags": [
            "No major visual inconsistency detected"
        ]
    }