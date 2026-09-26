from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_FILE = (
    PROJECT_ROOT
    / "datasets"
    / "sample_documents"
    / "passports"
    / "synthetic_valid_01.png"
)

image = Image.new("RGB", (1400, 900), "white")
draw = ImageDraw.Draw(image)

try:
    title_font = ImageFont.truetype("arial.ttf", 42)
    text_font = ImageFont.truetype("arial.ttf", 30)
    mrz_font = ImageFont.truetype("cour.ttf", 26)
except OSError:
    title_font = ImageFont.load_default()
    text_font = ImageFont.load_default()
    mrz_font = ImageFont.load_default()

lines = [
    ("SYNTHETIC PASSPORT TEST IMAGE", title_font),
    ("", text_font),
    ("Full Name: SAMPLE TRAVELER", text_font),
    ("Passport Number: A12345678", text_font),
    ("Nationality: IND", text_font),
    ("Date of Birth: 2002-08-12", text_font),
    ("Gender: F", text_font),
    ("Issue Date: 2022-05-10", text_font),
    ("Expiry Date: 2032-05-10", text_font),
    ("", text_font),
        ("P<IND" + "SAMPLE<<TRAVELER" + "<" * 23, mrz_font),
    ("A123456784IND0208127F3205105<<<<<<<<<<<<<<08", mrz_font),
]

y_position = 60

for line, font in lines:
    draw.text((70, y_position), line, fill="black", font=font)
    y_position += 65

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
image.save(OUTPUT_FILE)

print(f"Synthetic OCR test image created: {OUTPUT_FILE}")
