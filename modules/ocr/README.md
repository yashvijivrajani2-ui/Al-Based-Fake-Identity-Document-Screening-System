# Borderguard AI

A Python learning project that demonstrates a safe synthetic OCR-style workflow.

## Important Note

This project uses only synthetic placeholder data.

It does not process real passport images or real personal information.
The `VALID` status means only that required mock OCR fields are present.
It does not confirm that a real identity document is authentic or valid.

## Features

- Locates permitted sample image files in the passport test folder.
- Loads synthetic mock passport-style OCR data.
- Validates required OCR fields.
- Saves mock OCR and validation results as JSON.
- Includes automated validator tests.

## Project Structure

```text
Borderguard AI/
├── datasets/
│   └── sample_documents/
│       └── passports/
├── modules/
│   └── ocr/
│       ├── mock_ocr_output.py
│       ├── ocr_extractor.py
│       ├── ocr_validator.py
│       └── result_writer.py
├── outputs/
│   └── ocr_results/
│       └── mock_ocr_result.json
└── tests/
    └── test_ocr_validator.py
```

## Run the OCR Workflow

Open the terminal in the main project folder and run:

```powershell
py -m modules.ocr.ocr_extractor
```

This will:

1. Check the sample-documents folder.
2. Load synthetic mock OCR data.
3. Validate required fields.
4. Save the result as JSON.

## Run Automated Tests

Run:

```powershell
py -m unittest -v tests.test_ocr_validator
```

Expected result:

```text
Ran 2 tests
OK
```

## JSON Output

The synthetic result is saved here:

```text
outputs/ocr_results/mock_ocr_result.json
```