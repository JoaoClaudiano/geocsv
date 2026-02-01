import pdfplumber
from app.services.ocr import ocr_pdf
from app.services.pdf_reader import extract_text

def read_pdf_smart(pdf_path: str) -> dict:
    with pdfplumber.open(pdf_path) as pdf:
        text_sample = ""
        for page in pdf.pages[:2]:
            text_sample += page.extract_text() or ""

    # Heurística simples e segura
    if len(text_sample.strip()) < 50:
        return ocr_pdf(pdf_path)
    else:
        data = extract_text(pdf_path)
        data["source"] = "vector"
        return data
