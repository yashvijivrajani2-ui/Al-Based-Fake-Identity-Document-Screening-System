import unittest

from modules.ocr.mock_ocr_output import get_mock_passport_ocr
from modules.ocr.ocr_validator import validate_ocr_result


class TestOCRValidator(unittest.TestCase):
    def test_complete_mock_ocr_result_is_valid(self):
        mock_data = get_mock_passport_ocr()

        result = validate_ocr_result(mock_data)

        self.assertTrue(result["is_valid"])
        self.assertEqual(result["missing_fields"], [])

    def test_missing_passport_number_is_invalid(self):
        mock_data = get_mock_passport_ocr()
        mock_data["passport_number"] = ""

        result = validate_ocr_result(mock_data)

        self.assertFalse(result["is_valid"])
        self.assertIn("passport_number", result["missing_fields"])


if __name__ == "__main__":
    unittest.main()