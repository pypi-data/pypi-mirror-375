import pytesseract
from PIL import Image
from pathlib import Path
from pdf2image import convert_from_path


file_path = r"D:\Downloads\3.pdf"
images = convert_from_path(
    file_path, dpi=300, poppler_path=r"D:\Program Files\poppler-24.08.0\Library\bin"
)
target_path = Path("test/identity3/raw/")
target_path.mkdir(parents=True, exist_ok=True)

pytesseract.pytesseract.tesseract_cmd = r"D:\Program Files\Tesseract-OCR\tesseract.exe"

for i, img in enumerate(images):
    text = pytesseract.image_to_string(img, lang="nep")
    with open(target_path / f"text_page_{i+1}.txt", "w", encoding="utf-8") as f:
        f.write(text)

text = ""
for page in Path(target_path).glob("*.txt"):
    text += page.read_text(encoding="utf-8")
print(text)
(target_path / "full_text.txt").write_text(text, encoding="utf-8")