import pdfplumber

def extract_text(pdf_path: str) -> dict:
    pages_text = []

    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            pages_text.append({
                "page": i + 1,
                "text": text or ""
            })

    return {
        "pages": pages_text,
        "pages_count": len(pages_text)
    }
